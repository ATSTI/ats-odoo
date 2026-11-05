from odoo import models, fields

class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    analytic_account_id = fields.Many2one('account.analytic.account', string="Conta Analítica", readonly=True)

    def _select(self):
        return super()._select() + """,
            (SELECT key::integer FROM jsonb_each(line.analytic_distribution) LIMIT 1) AS analytic_account_id
        """