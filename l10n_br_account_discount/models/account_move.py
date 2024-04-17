# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, fields, models, api

class AccountMove(models.Model):
    _name = "account.move"
    _inherit = [
        _name,
        "l10n_br_fiscal.document.move.mixin",
    ]
    _inherits = {"l10n_br_fiscal.document": "fiscal_document_id"}
    _order = "date DESC, name DESC"

    amount_discount_value = fields.Monetary(
        string="Total do desconto",
        # compute="_compute_amount_one",
        store=True,
        inverse="_inverse_amount_discount",
    )

    @api.onchange("amount_discount_value")
    def _onchange_amount_discount_value(self):
        if not self.amount_discount_value or not self.amount_price_gross:
            return
        round_curr = self.currency_id.round
        self.amount_untaxed = self.amount_price_gross - self.amount_discount_value
        self.amount_total = self.amount_untaxed + self.amount_tax
        amount_untaxed_signed = self.amount_untaxed
        if (
            self.currency_id
            and self.company_id
            and self.currency_id != self.company_id.currency_id
        ):
            date = self.invoice_date or fields.Date.today()
            amount_untaxed_signed = self.currency_id._convert(
                self.amount_untaxed, self.company_id.currency_id, self.company_id, date
            )
        sign = self.move_type in ["in_invoice", "out_refund"] and -1 or 1
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign

    def _inverse_amount_discount(self):
        for record in self.filtered(lambda doc: doc._get_product_amount_lines()):
            amount_discount_value = record.amount_discount_value
            if all(record._get_product_amount_lines().mapped("discount_value")):
                amount_other_old = sum(
                    record._get_product_amount_lines().mapped("discount_value")
                )
                for line in record._get_product_amount_lines()[:-1]:
                    line.discount_value = amount_discount_value * (
                        line.discount_value / amount_other_old
                    )
                record._get_product_amount_lines()[
                    -1
                ].discount_value = amount_discount_value - sum(
                    line.discount_value
                    for line in record._get_product_amount_lines()[:-1]
                )
            else:
                amount_total = sum(
                    record._get_product_amount_lines().mapped("price_subtotal")
                )
                if len(record._get_product_amount_lines()) == 1:
                    for line in record._get_product_amount_lines():
                        line.discount_value = amount_discount_value
                        line._onchange_fiscal_taxes()
                        line._compute_amounts()
                for line in record._get_product_amount_lines()[:-1]:
                    if line.price_gross and amount_total:
                        line.discount_value = amount_discount_value * (
                            line.price_gross / amount_total
                        )
                record._get_product_amount_lines()[
                    -1
                ].discount_value = amount_discount_value - sum(
                    line.discount_value
                    for line in record._get_product_amount_lines()[:-1]
                )

            for line in record._get_product_amount_lines():
                line._onchange_fiscal_taxes()
                line._create_exchange_difference_move()
                line.update(line._get_price_total_and_subtotal())
                line._compute_amount_residual()
                # sem esta linha abaixo qdo edita nao calcula
                line.update(line._get_amount_credit_debit())
                
            record._fields["amount_total"].compute_value(record)
            record.write(
                {
                    name: value
                    for name, value in record._cache.items()
                    if record._fields[name].compute == "_amount_all"
                    and not record._fields[name].inverse
                }
            )
            record._recompute_dynamic_lines(recompute_all_taxes=True)
