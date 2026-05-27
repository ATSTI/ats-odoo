from odoo import models
from ast import literal_eval
from odoo import models

class ReportWaterReading(models.AbstractModel):
    _name = "report.condominio_access.report_water_reading_template"
    _description = "Relatório Leituras Água"

    def _get_report_values(self, docids, data=None):
        data = data or {}
        leituras = self.env["condo.water.reading"].browse(
            data.get("ids", [])
        )
        return {
            "doc_ids": leituras.ids,
            "doc_model": "condo.water.reading",
            "docs": leituras,
            "metro": data.get("metro", 0),
        }
    

class ReportWaterNotFound(models.AbstractModel):
    _name = 'report.condominio_access.report_water_not_found_template'
    _description = 'Relatório de Lotes Não Encontrados'

    def _get_report_values(self, docids, data=None):

        docs = self.env['condo.import.water.wizard'].browse(docids)

        report_lines = []

        for doc in docs:
            if doc.report_data:
                report_lines.extend(literal_eval(doc.report_data))

        return {
            'doc_ids': docids,
            'doc_model': 'condo.import.water.wizard',
            'docs': docs,
            'lines': report_lines,
        }