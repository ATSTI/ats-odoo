from odoo import models, fields, _
from odoo.exceptions import UserError
import base64
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

    def _normalizar_lote(self, lote):
        lote = str(lote).strip().upper()
        if "." in lote:
            numero, complemento = lote.split(".", 1)
            numero = numero.replace("-", "")
            lote = f"{numero}-{complemento}"
        else:
            lote = lote.replace("-", "")
        return lote

    def action_import(self):
        if not self.file:
            raise UserError("Envie um arquivo.")
        wb = openpyxl.load_workbook(
            BytesIO(base64.b64decode(self.file)),
            data_only=True)
        sheet = wb.worksheets[0]
        residence_model = self.env["condo.residence"]
        reading_model = self.env["condo.water.reading"]
        criados = 0
        atualizados = 0
        nao_encontrados = []
        for idx, row in enumerate(
            sheet.iter_rows(min_row=3, values_only=True),
            start=3
        ):  
            # import pudb;pudb.set_trace()
            lote = row[3]
            data_ref = row[5]
            anterior = row[6]
            atual = row[7]
            obs = row[9]
            proprietario = row[4] or ""
            if not lote:
                continue
            lote = self._normalizar_lote(lote)
            _logger.warning("Buscando lote: [%s]", lote)
            residence = residence_model.search([
                ("lote", "=", lote)
            ], limit=1)

            if not residence:
                nao_encontrados.append({
                    'linha': idx,
                    'lote': lote,
                    'proprietario': proprietario,})
                _logger.warning("NAO ACHOU lote: %s", lote)
                continue
            _logger.warning("ACHOU: %s", residence.name)
            if str(anterior).strip().lower() == "sem hidro":
                anterior = 0
                obs = 'Sem hidro'
            if str(atual).strip().lower() == "sem hidro":
                atual = 0
                obs = 'Sem hidro'
            if isinstance(data_ref, str):
                data_ref = datetime.strptime(
                    data_ref,
                    "%m/%Y"
                ).date()
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
                "obs": obs or "",}
            if existing:
                existing.write(vals)
                criados += 0
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