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
        for row in sheet.iter_rows(min_row=3, values_only=True):   
            lote = row[3]      
            data_ref = row[5]  
            anterior = row[6]  
            atual = row[7]
            obs = row[9]      
            if not lote:
                continue
            lote = self._normalizar_lote(lote)
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
