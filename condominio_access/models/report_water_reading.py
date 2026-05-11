# reports/report_water_reading.py

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