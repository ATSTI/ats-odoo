# Copyright (C) 2009 - TODAY Renato Lima - Akretion
# Copyright (C) 2019 - TODAY Raphaël Valyi - Akretion
# Copyright (C) 2020 - TODAY Luis Felipe Mileo - KMEE
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import mute_logger

class AccountMove(models.Model):
    _inherit = "account.move"

    amount_discount_value = fields.Monetary(
        string="Amount Discount",
        compute="_compute_amount",
        store=True,
        inverse="_inverse_amount_discount",
    )

    def _compute_amount(self):
        fields = self._get_amount_fields()
        for doc in self:
            values = {key: 0.0 for key in fields}
            for line in doc._get_amount_lines():
                for field in fields:
                    if field in line._fields.keys():
                        values[field] += line[field]
                    if field.replace("amount_", "") in line._fields.keys():
                        # FIXME this field creates an error in invoice form
                        if field == "amount_financial_discount_value":
                            values[
                                "amount_financial_discount_value"
                            ] += 0  # line.financial_discount_value
                        else:
                            values[field] += line[field.replace("amount_", "")]

            # Valores definidos pelo Total e não pela Linha
            if (
                doc.company_id.delivery_costs == "total"
                or doc.force_compute_delivery_costs_by_total
            ):
                values["amount_freight_value"] = doc.amount_freight_value
                values["amount_insurance_value"] = doc.amount_insurance_value
                values["amount_other_value"] = doc.amount_other_value
                values["amount_discount_value"] = doc.amount_discount_value

            doc.update(values)

    def _inverse_amount_discount(self):
        import wdb;
        wdb.set_trace()
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
                for line in record._get_product_amount_lines()[:-1]:
                    if line.price_subtotal and amount_total:
                        line.discount_value = amount_discount_value * (
                            line.price_subtotal / amount_total
                        )
                # record._get_product_amount_lines()[
                #     -1
                # ].discount_value = amount_discount_value - sum(
                #     line.discount_value
                #     for line in record._get_product_amount_lines()[:-1]
                # )
            for line in record._get_product_amount_lines():
                line._onchange_fiscal_taxes()
            record._fields["amount_total"].compute_value(record)
            record.write(
                {
                    name: value
                    for name, value in record._cache.items()
                    if record._fields[name].compute == "_amount_all"
                    and not record._fields[name].inverse
                }
            )

   