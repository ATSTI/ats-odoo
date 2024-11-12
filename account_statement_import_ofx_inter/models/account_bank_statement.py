# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import _, api, models


class AccountBankStatementLine(models.Model):

    _inherit = "account.bank.statement.line"

    def write(self, vals):
        # partner esta sendo removido, isso evita isso
        if "partner_id" in vals and vals == {"partner_id": False}:
            vals = {}
        return super().write(vals)

