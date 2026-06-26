from odoo import models, fields, _
from odoo.exceptions import UserError
import base64
import re
import openpyxl
from io import BytesIO
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class CondoImportWaterWizard(models.TransientModel):
    _name = "condo.import.water.wizard"
    _description = "Importar Leituras de Água"

    file = fields.Binary(string="Arquivo Excel", required=True)
    filename = fields.Char()

    report_data = fields.Text()

    def _chave_lote(self, lote):
        """Gera uma chave canônica para comparar lotes, ignorando
        diferenças de formatação (-, ., espaços, maiúsc/minúsc).
        Ex: 'A-06.B', 'A06-B' e 'a 06 b' geram todos 'A06B'.
        """
        if lote is None:
            return ""
        texto = str(lote).strip().upper()
        # Excel converte lote 100% numérico em float (ex: 6 -> '6.0')
        if texto.endswith(".0"):
            texto = texto[:-2]
        # mantém só letras e números
        return re.sub(r"[^A-Z0-9]", "", texto)

    def _montar_indice_residencias(self):
        """{chave_normalizada: [residences]} com todos os lotes cadastrados.
        Evita um search() por linha e detecta lotes ambíguos."""
        residences = self.env["condo.residence"].search([])
        indice = {}
        for r in residences:
            chave = self._chave_lote(r.lote)
            indice.setdefault(chave, []).append(r)
        return indice

    def action_import(self):
        if not self.file:
            raise UserError("Envie um arquivo.")
        wb = openpyxl.load_workbook(
            BytesIO(base64.b64decode(self.file)),
            data_only=True)
        sheet = wb.worksheets[0]
        reading_model = self.env["condo.water.reading"]
        indice_residencias = self._montar_indice_residencias()
        _logger.warning("Índice de residências montado com %s chaves", len(indice_residencias))

        criados = 0
        atualizados = 0
        nao_encontrados = []

        for idx, row in enumerate(
            sheet.iter_rows(min_row=3, values_only=True),
            start=3
        ):
            lote_original = row[3]
            data_ref = row[5]
            anterior = row[6]
            atual = row[7]
            obs = row[9]
            proprietario = row[4] or ""

            if not lote_original:
                continue

            chave = self._chave_lote(lote_original)
            candidatos = indice_residencias.get(chave, [])

            if not candidatos:
                nao_encontrados.append({
                    'linha': idx,
                    'lote': lote_original,
                    'proprietario': proprietario,
                })
                _logger.warning("NAO ACHOU lote: %s (chave: %s)", lote_original, chave)
                continue

            if len(candidatos) > 1:
                nomes = ", ".join(c.lote for c in candidatos)
                nao_encontrados.append({
                    'linha': idx,
                    'lote': f"{lote_original} (AMBÍGUO: {nomes})",
                    'proprietario': proprietario,
                })
                _logger.warning(
                    "Lote AMBIGUO: %s (chave: %s) bate com %s",
                    lote_original, chave, nomes
                )
                continue

            residence = candidatos[0]
            _logger.warning("ACHOU: %s (lote planilha: %s)", residence.name, lote_original)

            if str(anterior).strip().lower() == "sem hidro":
                anterior = 0
                obs = 'Sem hidro'
            if str(atual).strip().lower() == "sem hidro":
                atual = 0
                obs = 'Sem hidro'

            if isinstance(data_ref, str):
                data_ref = datetime.strptime(data_ref, "%m/%Y").date()
            elif isinstance(data_ref, datetime):
                data_ref = data_ref.date()

            existing = reading_model.search([
                ("residence_id", "=", residence.id),
                ("data_referencia", "=", data_ref)
            ], limit=1)

            vals = {
                "residence_id": residence.id,
                "data_referencia": data_ref,
                "anterior": float(0 if str(anterior).strip() in ("", "-", "None") else anterior),
                "atual": float(0 if str(atual).strip() in ("", "-", "None") else atual),
                "obs": obs or "",
            }

            if existing:
                existing.write(vals)
                atualizados += 1
                _logger.warning("Atualizado: %s", residence.name)
            else:
                reading_model.create(vals)
                criados += 1
                _logger.warning("Criado: %s", residence.name)

        self.report_data = str(nao_encontrados)

        if nao_encontrados:
            return self.env.ref(
                'condominio_access.action_report_water_not_found'
            ).report_action(self)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Importação concluída'),
                'message': (
                    f'Criados: {criados} | '
                    f'Atualizados: {atualizados} | '
                    f'Não encontrados: 0'
                ),
                'sticky': True,
                'type': 'success',
            }
        }