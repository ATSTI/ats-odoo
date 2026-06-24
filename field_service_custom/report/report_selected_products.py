from odoo import models


class ReportSelectedProducts(models.AbstractModel):
    _name = "report.field_service_custom.report_selected_products_document"

    def _get_report_values(self, docids, data=None):
        data = data or {}
        move = self.env["account.move"].browse(data.get("move_id"))
        lines = self.env["account.move.line"].browse(data.get("move_line_ids", [])).exists()
        return {
            "doc": move,
            "lines": lines,
            "currency": move.currency_id,
        }