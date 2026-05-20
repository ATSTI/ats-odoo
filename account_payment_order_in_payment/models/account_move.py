# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    # adicionado aqui pra evitar que fique "Em pagamento" quando a fatura for baixada manualmente
    @api.model
    def _get_invoice_in_payment_state(self):
        if self.line_ids.payment_line_ids:
            if self.line_ids.payment_line_ids.state == "cancel":
                return "paid"
            return "in_payment"
        return super()._get_invoice_in_payment_state()
