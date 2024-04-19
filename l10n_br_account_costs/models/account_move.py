# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models
from collections import defaultdict


class AccountMove(models.Model):
    _name = "account.move"
    _inherit = [
        _name,
        "l10n_br_fiscal.document.move.mixin",
    ]
    _inherits = {"l10n_br_fiscal.document": "fiscal_document_id"}
    _order = "date DESC, name DESC"
    
    amount_freight_value = fields.Monetary(
        string="Frete",
        # compute="_compute_amount",
        # store=True,
        inverse="_inverse_amount_freight",
    )
    
    amount_insurance_value = fields.Monetary(
        string="Seguro",
        # compute="_compute_amount",
        # store=True,
        inverse="_inverse_amount_insurance",
    )

    amount_other_value = fields.Monetary(
        string="Outro",
        # compute="_compute_amount",
        # store=True,
        inverse="_inverse_amount_other",
    )

    amount_icms_relief_value = fields.Monetary(
        inverse="_inverse_amount_icms_relief",
        compute="_compute_amount",
        store=True,
    )

    def _get_amount_lines(self):
        """Get object lines instaces used to compute fields"""
        return self.mapped("line_ids")

    @api.depends("line_ids.price_subtotal")
    def _amount_all(self):
        """Compute the total amounts of the SO."""
        for order in self:
            order._compute_amount()

    def _inverse_amount_freight(self):
        res = super()._inverse_amount_freight()
        for line in self.invoice_line_ids:
            line._onchange_price_subtotal()
        self._recompute_payment_terms_lines()
        return res

    def _inverse_amount_other(self):
        res = super()._inverse_amount_other()
        for line in self.invoice_line_ids:
            line._onchange_price_subtotal()
        self._recompute_payment_terms_lines()
        return res

    def _inverse_amount_insurance(self):
        res = super()._inverse_amount_insurance()
        for line in self.invoice_line_ids:
            line._onchange_price_subtotal()
        self._recompute_payment_terms_lines()
        return res

    @api.onchange("amount_freight_value","amount_insurance_value","amount_other_value")
    def _onchange_amount_freight_value(self):
        self._compute_amount()
        if self.amount_freight_value:
            self._inverse_amount_freight()

        if self.amount_insurance_value:
            self._inverse_amount_insurance()

        if self.amount_other_value:
            self._inverse_amount_other()

    # def _calc_inverse_amount(self):       
    #     if len(self) > 1:
    #         return
    #     for move in self:
    #         move._compute_amount()
    #         if move.payment_state == 'invoicing_legacy':
    #             move.payment_state = move.payment_state
    #             continue
    #         # se ja existe tem q excluir
    #         insurance = 0.0
    #         other = 0.0
    #         freight = 0.0
    #         for line in move.line_ids:
    #             if not line.exclude_from_invoice_tab and line.insurance_value > 0:
    #                 insurance += line.insurance_value
    #             if not line.exclude_from_invoice_tab and line.freight_value > 0:
    #                 freight += line.freight_value
    #             if not line.exclude_from_invoice_tab and line.other_value > 0:
    #                 other += line.other_value
    #         remove = False
    #         for line in move.line_ids:    
    #             if line.name in ["[SEGURO]", "[FRETE]", "[OUTROS]"]:
    #                 remove = True
    #                 move.with_context(
    #                     check_move_validity=False,
    #                     skip_account_move_synchronization=True,
    #                     force_delete=True,
    #                 ).write(
    #                     {
    #                         "line_ids": [(2, line.id)],
    #                         "to_check": False,
    #                     }
    #                 )
    #         if remove:
    #             move.with_context(check_move_validity=False)._onchange_currency()
    #         new_line = False
    #         if insurance:
    #             new_line = self.env["account.move.line"].new(
    #                     {
    #                         "name": "[SEGURO]",
    #                         "account_id": move.company_id.acc_insurance_id.id or line.account_id.id,
    #                         "move_id": self.id,
    #                         "exclude_from_invoice_tab": True,
    #                         "price_unit": insurance,
    #                     }
    #             )
    #             move.line_ids += new_line
    #         if other:
    #             new_line = self.env["account.move.line"].new(
    #                     {
    #                         "name": "[OUTROS]",
    #                         "account_id": move.company_id.acc_other_id.id or line.account_id.id,
    #                         "move_id": self.id,
    #                         "exclude_from_invoice_tab": True,
    #                         "price_unit": other,
    #                     }
    #             )
    #             move.line_ids += new_line
    #         if freight:
    #             new_line = self.env["account.move.line"].new(
    #                     {
    #                         "name": "[FRETE]",
    #                         "account_id": move.company_id.acc_freight_id.id or line.account_id.id,
    #                         "move_id": self.id,
    #                         "exclude_from_invoice_tab": True,
    #                         "price_unit": freight,
    #                     }
    #             )
    #             move.line_ids += new_line
    #         if new_line:
    #             move.with_context(check_move_validity=False)._onchange_currency()
    #             in_invoices = self.filtered(lambda m: m.move_type == 'in_invoice')
    #             out_invoices = self.filtered(lambda m: m.move_type == 'out_invoice')
    #             for line in move.line_ids:
    #                 if out_invoices and line.credit:
    #                     line.credit -= line.freight_value + line.insurance_value + line.other_value - line.discount_value
    #                 if in_invoices and line.debit:
    #                     line.debit += line.freight_value + line.insurance_value + line.other_value - line.discount_value
    #                 if line.name ==  "[SEGURO]":
    #                     if out_invoices:
    #                         line.credit = insurance
    #                     if in_invoices:
    #                         line.debit = insurance
    #                 if line.name ==  "[FRETE]":
    #                     if out_invoices:
    #                         line.credit = freight
    #                     if in_invoices:
    #                         line.debit = freight
    #                 if line.name ==  "[OUTROS]":
    #                     if out_invoices:
    #                         line.credit = other
    #                     if in_invoices:
    #                         line.debit = other
    #             move._recompute_dynamic_lines(recompute_all_taxes=True)

    @api.depends('amount_icms_relief_value')
    def _inverse_amount_icms_relief(self):
        if len(self) > 1:
            return
        if self.move_type not in ('in_invoice','out_invoice'):
            return
        for move in self:
            if move.payment_state == 'invoicing_legacy':
                move.payment_state = move.payment_state
                continue
            for line in move.line_ids:
                if line.name in ["[DESONERACAO]"]:
                    move.with_context(
                        check_move_validity=False,
                        skip_account_move_synchronization=True,
                        force_delete=True,
                    ).write(
                        {
                            "line_ids": [(2, line.id)],
                            "to_check": False,
                        }
                    )
            for line in move.line_ids:
                if not line.exclude_from_invoice_tab and line.icms_relief_value > 0:
                    if line.icms_relief_value:
                        new_line = self.env["account.move.line"].new(
                            {
                                "name": "[DESONERACAO]",
                                "account_id": line.account_id.id,
                                "move_id": self.id,
                                "exclude_from_invoice_tab": True,
                                "price_unit": -line.icms_relief_value,
                            }
                        )
                    move.line_ids += new_line
                    move.with_context(check_move_validity=False)._onchange_currency()


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.onchange('quantity', 'discount', 'price_unit', 'tax_ids', 'freight_value', 'other_value', 'insurance_value')
    def _onchange_price_subtotal(self):
        result = super()._onchange_price_subtotal()
        self.move_id._recompute_dynamic_lines(recompute_all_taxes=True)
        return result
