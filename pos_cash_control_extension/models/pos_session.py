# Copyright 2024 Antoni Marroig(APSL-Nagarro)<amarroig@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, _
from odoo.tools import plaintext2html


class PosSession(models.Model):
    _inherit = "pos.session"

    def _set_opening_control_data(self, cashbox_value: int, notes: str):
        self.state = "opened"
        self.start_at = fields.Datetime.now()

        cash_payment_method_ids = self.config_id.payment_method_ids.filtered(
            lambda pm: pm.is_cash_count
        )
        if notes:
            self.opening_notes = notes
        if cash_payment_method_ids:
            self._post_cash_details_message(
                "Opening cash", self.cash_register_balance_start, notes
            )
            self.cash_register_balance_start = cashbox_value
        elif notes:
            message = _("Opening control message: ")
            message += notes
            self.message_post(body=plaintext2html(message))

    def _post_cash_details_message(self, state, difference, notes):
        expected = self.cash_register_balance_start
        expected_formatted = self.currency_id.format(expected)
        difference_formatted = self.currency_id.format(difference)
        counted_formatted = self.currency_id.format(expected + difference)

        if state == "Opening cash":
            message = _("Opening cash difference: %s \n", difference_formatted)
            message += _("Opening cash expected: %s \n", expected_formatted)
            message += _("Opening cash counted: %s \n", counted_formatted)
        else:
            message = _("Closing difference: %s \n", 0.0)
            message += _("Closing expected: %s \n", counted_formatted)
            message += _("Closing counted: %s \n", counted_formatted)

        if notes:
            message += _("Opening control message: ")
            message += notes
        if message:
            self.message_post(body=plaintext2html(message))

    def _get_closed_orders(self):
        return self.order_ids.filtered(lambda o: o.state not in ['draft', 'cancel'])

    def get_closing_control_data(self):
        res = super().get_closing_control_data()
        orders = self._get_closed_orders()
        cash_payment_method_ids = self.payment_method_ids.filtered(
            lambda pm: pm.type == "cash"
        )
        default_cash_payment_method_id = (
            cash_payment_method_ids[0] if cash_payment_method_ids else None
        )
        payments = orders.payment_ids.filtered(
            lambda p: p.payment_method_id.type != "pay_later"
        )
        total_default_cash_payment_amount = (
            sum(
                payments.filtered(
                    lambda p: p.payment_method_id == default_cash_payment_method_id
                ).mapped("amount")
            )
            if default_cash_payment_method_id
            else 0
        )
        if "default_cash_details" in res and res["default_cash_details"]:
            res["default_cash_details"]["opening"] = self.cash_register_balance_start
            res["default_cash_details"]["amount"] = (
                self.cash_register_balance_start
                + total_default_cash_payment_amount
                + sum(self.sudo().statement_line_ids.mapped("amount"))
            )
        return res

    def _post_statement_difference(self, amount, is_opening):
        pass

    def post_closing_cash_details(self, counted_cash):
        res = super().post_closing_cash_details(counted_cash)
        self.cash_register_balance_end_real = self.cash_register_balance_start or 0.0
        return res
