# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models

class ReportSaleBalanceWizard(models.TransientModel):
    _name = "report.sale.balance.wizard"
    _description = "Report Balance Wizard"

    date_start = fields.Date('Data Inicial')
    date_end = fields.Date('Data Final')

    def action_report_balance(self):
        data = {
            'date_start': self.date_start,
            'date_end': self.date_end,
        }
        docargs = {
            'data': data,
        }
        return self.env.ref('report_sale_balance.action_report_sale_balance').report_action(None, data=docargs)