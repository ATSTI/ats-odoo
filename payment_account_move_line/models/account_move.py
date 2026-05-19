# -*- coding: utf-8 -*-

from odoo import api, models, _


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # adicionado aqui pra evitar que fique "Em pagamento" quando a fatura for baixada usando outro metodo
    @api.model
    def _get_invoice_in_payment_state(self):
        """Called from _compute_payment_state method.
        Consider in_payment all the moves that are included in a payment order.
        """
        if self.line_ids.payment_line_ids:
            if self.line_ids.payment_line_ids.state == "cancel":
                return "paid"

            return "in_payment"
        return super()._get_invoice_in_payment_state()
