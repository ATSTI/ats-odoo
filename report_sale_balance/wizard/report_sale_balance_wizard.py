# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ReportSaleBalanceWizard(models.TransientModel):
    _name = "report.sale.balance.wizard"
    _description = "Report Balance Wizard"

    date_start = fields.Date('Data Inicial')
    date_end = fields.Date('Data Final')

    # def _get_report_values(self, docids, data=None):
    #     import pudb;pu.db
    #     docs = self.env['sale.order'].search([("date_order", ">=", self.date_start),("date_order", "<=", self.date_end)])
    #     return {
    #         'doc_ids': docids,
    #           'doc_model': 'sale.order',
    #           'docs': docs,
    #           'data': data,
    #     }

    def action_report_balance(self):
        # docs = self.env['sale.order'].search([("date_order", ">=", self.date_start),("date_order", "<=", self.date_end)])
        # return {
        #     'type': 'ir.actions.act_window',
        #     'view_mode': 'form',
        #     'res_model': 'sale.order',
        #     'docs': docs,
        #     'views': [(False, 'form')],
        #     'context': '',
        #     'view_id': False,
        # }
        data = {
            'date_start': self.date_start,
            'date_end': self.date_end,
        }
        docargs = {
            'data': data,
        }
            # 'doc_ids': docs.ids,
            # 'doc_model': 'sale.order',
            # 'docs': docs,

        # import pudb;pu.db
        return self.env.ref('report_sale_balance.action_report_sale_balance').report_action(None, data=docargs)