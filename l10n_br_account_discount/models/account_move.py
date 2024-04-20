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
        inverse="_inverse_amount_discount",
    )

    @api.onchange("amount_discount_value")
    def _onchange_amount_discount_value(self):
        self._compute_amount()
        self._inverse_amount_discount()
        if self.amount_discount_value:
            for record in self.filtered(lambda doc: doc._get_product_amount_lines()):
                for line in record.invoice_line_ids:
                    line._onchange_price_subtotal()
                record._recompute_payment_terms_lines()

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
            record._fields["amount_total"].compute_value(record)
            record.write(
                {
                    name: value
                    for name, value in record._cache.items()
                    if record._fields[name].compute == "_amount_all"
                    and not record._fields[name].inverse
                }
            )


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.onchange('quantity', 'discount', 'price_unit', 'tax_ids', 'freight_value', 'other_value', 'insurance_value', 'discount_value')
    def _onchange_price_subtotal(self):
        result = super()._onchange_price_subtotal()
        self.move_id._recompute_dynamic_lines(recompute_all_taxes=True)
        return result