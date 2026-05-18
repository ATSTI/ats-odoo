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

    def _normalizar_lote(self, lote, quadra):
        lote = str(lote).strip().upper()
        quadra = str(quadra).strip().upper()

        if "." in lote:
            numero, complemento = lote.split(".", 1)
            numero = numero.zfill(2)  # garante 2 dígitos
            lote = f"{quadra}{numero}-{complemento}"

        return lote

    def action_import(self):
        if not self.file:
            raise UserError("Envie um arquivo.")

        wb = openpyxl.load_workbook(
            BytesIO(base64.b64decode(self.file)),
            data_only=True
        )

        sheet = wb.worksheets[0]

        residence_model = self.env["condo.residence"]
        reading_model = self.env["condo.water.reading"]
        import pudb; pudb.set_trace()
        for row in sheet.iter_rows(min_row=3, values_only=True):

            obs = ""   
            quadra = row[0]
            lote = row[1]      
            data_ref = row[2]  
            anterior = row[6]  
            atual = row[7]      

            if not lote:
                continue

            lote = self._normalizar_lote(lote,quadra)

            _logger.warning("Buscando lote: [%s]", lote)

            residence = residence_model.search([
                ("lote", "=", lote)
            ], limit=1)

            if not residence:
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
                "anterior": float(anterior or 0),
                "atual": float(atual or 0),
                "obs": obs or "",
            }

            if existing:
                existing.write(vals)
                _logger.warning("Atualizado: %s", residence.name)
            else:
                reading_model.create(vals)
                _logger.warning("Criado: %s", residence.name)
