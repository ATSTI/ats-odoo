# Copyright (C) 2009  Renato Lima - Akretion
# Copyright (C) 2012  Raphaël Valyi - Akretion
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
        compute="_compute_amount",
        store=True,
        inverse="_inverse_amount_freight",
    )
    
    amount_insurance_value = fields.Monetary(
        string="Seguro",
        compute="_compute_amount",
        store=True,
        inverse="_inverse_amount_insurance",
    )

    amount_other_value = fields.Monetary(
        string="Outro",
        compute="_compute_amount",
        store=True,
        inverse="_inverse_amount_other",
    )

    amount_icms_relief_value = fields.Monetary(
        inverse="_inverse_amount_icms_relief",
        compute="_compute_amount",
        store=True,
    )

    def _inverse_amount_freight(self):
        super()._inverse_amount_freight()
        self._calc_inverse_amount()
        self._compute_amount()

    def _inverse_amount_other(self):
        super()._inverse_amount_other()
        self._calc_inverse_amount()
        self._compute_amount()

    def _inverse_amount_insurance(self):
        super()._inverse_amount_insurance()
        self._calc_inverse_amount()
        self._compute_amount()

    def _calc_inverse_amount(self):
        if len(self) > 1:
            return
        for move in self:
            if move.payment_state == 'invoicing_legacy':
                move.payment_state = move.payment_state
                continue
            # se ja existe tem q excluir
            remove = False
            for line in move.line_ids:
                if line.name in ["[SEGURO]", "[FRETE]", "[OUTROS]"]:
                    remove = True
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
            if remove:
                move.with_context(check_move_validity=False)._onchange_currency()
            insurance = 0.0
            other = 0.0
            freight = 0.0
            for line in move.line_ids: 
                if not line.exclude_from_invoice_tab and line.insurance_value > 0:
                    insurance += line.insurance_value
                if not line.exclude_from_invoice_tab and line.freight_value > 0:
                    freight += line.freight_value
                if not line.exclude_from_invoice_tab and line.other_value > 0:
                    other += line.other_value
            new_line = False
            if insurance:
                new_line = self.env["account.move.line"].new(
                        {
                            "name": "[SEGURO]",
                            "account_id": move.company_id.acc_insurance_id.id or line.account_id.id,
                            "move_id": self.id,
                            "exclude_from_invoice_tab": True,
                            "price_unit": insurance,
                        }
                )
                move.line_ids += new_line
            if other:
                new_line = self.env["account.move.line"].new(
                        {
                            "name": "[OUTROS]",
                            "account_id": move.company_id.acc_other_id.id or line.account_id.id,
                            "move_id": self.id,
                            "exclude_from_invoice_tab": True,
                            "price_unit": other,
                        }
                )
                move.line_ids += new_line
            if freight:
                new_line = self.env["account.move.line"].new(
                        {
                            "name": "[FRETE]",
                            "account_id": move.company_id.acc_freight_id.id or line.account_id.id,
                            "move_id": self.id,
                            "exclude_from_invoice_tab": True,
                            "price_unit": freight,
                        }
                )
                move.line_ids += new_line
            if new_line:
                move.with_context(check_move_validity=False)._onchange_currency()
                # in_invoices = self.filtered(lambda m: m.move_type == 'in_invoice')
                # out_invoices = self.filtered(lambda m: m.move_type == 'out_invoice')
                for line in move.line_ids:
                    # line._update_taxes()
                    # Call mixin compute method
                    # line._compute_amounts()
                    if line.credit:
                        line.credit -= line.freight_value + line.insurance_value + line.other_value
                    if line.name ==  "[SEGURO]":
                        line.credit = insurance
                    if line.name ==  "[FRETE]":
                        line.credit = freight
                    if line.name ==  "[OUTROS]":
                        line.credit = other
                    # line._update_taxes()
                    # line._onchange_mark_recompute_taxes()                  
                    # line._onchange_fiscal_tax_ids()
                    # line.update(line._get_price_total_and_subtotal())
                    # # line.update(line._get_amount_credit_debit())
                    # line.update(
                    #     {
                    #         "price_subtotal": line.amount_untaxed,
                    #         "price_gross": line.amount_untaxed + line.discount_value,
                    #         "price_total": line.amount_total,
                    #     }
                    # )
                # for item in move.invoice_line_ids:
                # for line in move.invoice_line_ids:
                #     line._onchange_fiscal_operation_id()
                move._recompute_dynamic_lines(recompute_all_taxes=True)
                # move.compute_taxes()
                # import pudb;pu.db
                # move._recompute_payment_terms_lines()
                # move._compute_amount()
                # move.with_context(check_move_validity=False)._onchange_currency()

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

    # @api.onchange('invoice_line_ids')
    # def _onchange_invoice_line_ids(self):
    #     import pudb;pu.db
    #     result = super()._onchange_invoice_line_ids()
    #     for record in self:
    #         if record.amount_freight_value > 0.0:
    #             for line in record.invoice_line_ids:
    #                 line.write({"freight_value": 0.0})
    #     # import pudb;pu.db
    #     self._inverse_amount_freight()
    #     return result
    
    # def write(self, values):       
    #     if 'invoice_line_ids' in values:
    #         # print (values['invoice_line_ids'])
    #         # for line in values['invoice_line_ids']:
    #         #     print ('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
    #         #     print (line)
    #         # for line in values['invoice_line_ids']:
    #         #     print ('===============================================')
    #         #     # if len(line[2])
    #         #     print (line[2])
    #         # import pudb;pu.db
    #         if self.amount_freight_value > 0.0:
    #             for line in values['invoice_line_ids']:
    #                 line[2].update({'freight_value': 0.0})
    #             self._inverse_amount_freight()
    #         # for line in values['invoice_line_ids']:
    #         #     print ('===============================================')
    #         #     print (line[2])
    #             # print (values['invoice_line_ids'])
    #     result = super().write(values)
    #     return result


    # def _compute_new_invoice_quantity(self, invoice_move):
    #     result = super()._compute_new_invoice_quantity(invoice_move=invoice_move)
    #     import pudb;pu.db
    #     if invoice_move:
    #         for line in invoice_move.invoice_line_ids:
    #             line.write({"fiscal_quantity": line.quantity})
    #             line._onchange_fiscal_tax_ids()
    #         invoice_move._onchange_invoice_line_ids()
    #     return result

    @api.depends(
        'line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'line_ids.full_reconcile_id',
        'line_ids.freight_value',
        'line_ids.insurance_value',
        'line_ids.other_value',
        'line_ids.icms_relief_value'
    )
    def _compute_amount(self):
        in_invoices = self.filtered(lambda m: m.move_type == 'in_invoice')
        out_invoices = self.filtered(lambda m: m.move_type == 'out_invoice')
        others = self.filtered(lambda m: m.move_type not in ('in_invoice', 'out_invoice'))
        reversed_mapping = defaultdict(lambda: self.env['account.move'])
        for reverse_move in self.env['account.move'].search([
            ('state', '=', 'posted'),
            '|', '|',
            '&', ('reversed_entry_id', 'in', in_invoices.ids), ('move_type', '=', 'in_refund'),
            '&', ('reversed_entry_id', 'in', out_invoices.ids), ('move_type', '=', 'out_refund'),
            '&', ('reversed_entry_id', 'in', others.ids), ('move_type', '=', 'entry'),
        ]):
            reversed_mapping[reverse_move.reversed_entry_id] += reverse_move

        caba_mapping = defaultdict(lambda: self.env['account.move'])
        caba_company_ids = self.company_id.filtered(lambda c: c.tax_exigibility)
        reverse_moves_ids = [move.id for moves in reversed_mapping.values() for move in moves]
        for caba_move in self.env['account.move'].search([
            ('tax_cash_basis_move_id', 'in', self.ids + reverse_moves_ids),
            ('state', '=', 'posted'),
            ('move_type', '=', 'entry'),
            ('company_id', 'in', caba_company_ids.ids)
        ]):
            caba_mapping[caba_move.tax_cash_basis_move_id] += caba_move

        for move in self:

            if move.payment_state == 'invoicing_legacy':
                # invoicing_legacy state is set via SQL when setting setting field
                # invoicing_switch_threshold (defined in account_accountant).
                # The only way of going out of this state is through this setting,
                # so we don't recompute it here.
                move.payment_state = move.payment_state
                continue

            total_untaxed = 0.0
            total_untaxed_currency = 0.0
            total_tax = 0.0
            total_tax_currency = 0.0
            total_to_pay = 0.0
            total_residual = 0.0
            total_residual_currency = 0.0
            total = 0.0
            total_currency = 0.0
            total_other = 0.0
            total_relief = 0.0
            currencies = move._get_lines_onchange_currency().currency_id
            for line in move.line_ids:
                if move.is_invoice(include_receipts=True):
                    total_relief += line.icms_relief_value
                    total_other += line.freight_value + line.insurance_value + line.other_value - line.icms_relief_value
                    # === Invoices ===

                    if not line.exclude_from_invoice_tab:
                        # Untaxed amount.
                        total_untaxed += line.balance
                        total_untaxed_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.tax_line_id:
                        # Tax amount.
                        total_tax += line.balance
                        total_tax_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.account_id.user_type_id.type in ('receivable', 'payable'):
                        # Residual amount.
                        total_to_pay += line.balance
                        total_residual += line.amount_residual
                        total_residual_currency += line.amount_residual_currency
                    if total_other:
                        # TODO melhorar este if
                        if total > 0:
                            total += total_other - total_relief
                            total_currency += total_other - total_relief
                        else:
                            total -= total_other
                            total_currency -= total_other
                        total_other = 0.0
                        
                else:
                    # === Miscellaneous journal entry ===
                    if line.debit:
                        total += line.balance
                        total_currency += line.amount_currency

            if move.move_type == 'entry' or move.is_outbound():
                sign = 1
            else:
                sign = -1
            move.amount_icms_relief_value = total_relief
            move.amount_untaxed = sign * (total_untaxed_currency if len(currencies) == 1 else total_untaxed)
            move.amount_tax = sign * (total_tax_currency if len(currencies) == 1 else total_tax)
            move.amount_total = sign * (total_currency if len(currencies) == 1 else total)
            move.amount_residual = -sign * (total_residual_currency if len(currencies) == 1 else total_residual)
            move.amount_untaxed_signed = -total_untaxed
            move.amount_tax_signed = -total_tax
            move.amount_total_signed = abs(total) if move.move_type == 'entry' else -total
            move.amount_residual_signed = total_residual

            currency = len(currencies) == 1 and currencies or move.company_id.currency_id

            # Compute 'payment_state'.
            new_pmt_state = 'not_paid' if move.move_type != 'entry' else False

            if move.is_invoice(include_receipts=True) and move.state == 'posted':

                if currency.is_zero(move.amount_residual):
                    reconciled_payments = move._get_reconciled_payments()
                    if not reconciled_payments or all(payment.is_matched for payment in reconciled_payments):
                        new_pmt_state = 'paid'
                    else:
                        new_pmt_state = move._get_invoice_in_payment_state()
                elif currency.compare_amounts(total_to_pay, total_residual) != 0:
                    new_pmt_state = 'partial'

            if new_pmt_state == 'paid' and move.move_type in ('in_invoice', 'out_invoice', 'entry'):
                reverse_moves = reversed_mapping[move]
                caba_moves = caba_mapping[move]
                for reverse_move in reverse_moves:
                    caba_moves |= caba_mapping[reverse_move]

                # We only set 'reversed' state in cas of 1 to 1 full reconciliation with a reverse entry; otherwise, we use the regular 'paid' state
                # We ignore potentials cash basis moves reconciled because the transition account of the tax is reconcilable
                reverse_moves_full_recs = reverse_moves.mapped('line_ids.full_reconcile_id')
                if reverse_moves_full_recs.mapped('reconciled_line_ids.move_id').filtered(lambda x: x not in (caba_moves + reverse_moves + reverse_moves_full_recs.mapped('exchange_move_id'))) == move:
                    new_pmt_state = 'reversed'

            move.payment_state = new_pmt_state
    
    # @api.returns('self', lambda value: value.id)
    # def copy(self, default=None):
    #     import pudb;pu.db
    #     move = super().copy(default)
    #     move.with_context(check_move_validity=False)._onchange_currency()
    #     return move
            
    # @api.model
    # def _move_autocomplete_invoice_lines_create(self, vals_list):
    #     new_lines = super()._move_autocomplete_invoice_lines_create(vals_list)
    #     # import pudb;pu.db
    #     #  necessario para o COPY
    #     # RODANDO SOMENTE EM NOTA DE SAIDA FAZER PARA ENTRADA

    #     for lines in new_lines:
    #         total = 0.0
    #         i = 0
    #         remove = False
    #         for line in lines['line_ids']:
    #             if line[2]['name'] and 'FRETE' in line[2]['name']:
    #                 remove = True
    #                 total += line[2]['credit']
    #                 break
    #             i += 1
    #         if remove:
    #             del lines['line_ids'][i]
    #         i = 0
    #         remove = False
    #         for line in lines['line_ids']:
    #             if line[2]['name'] and 'OUTRO' in line[2]['name']:
    #                 remove = True
    #                 total += line[2]['credit']
    #                 break
    #             i += 1
    #         if remove:
    #             del lines['line_ids'][i]
    #         i = 0
    #         remove = False
    #         for line in lines['line_ids']:
    #             if line[2]['name'] and 'SEGURO' in line[2]['name']:
    #                 remove = True
    #                 total += line[2]['credit']
    #                 break
    #             i += 1
    #         if remove:
    #             del lines['line_ids'][i]

    #         for line in lines['line_ids']:
    #             if total:
    #                 if line[2]['debit']:
    #                     line[2]['debit'] = line[2]['debit'] - total
    #                 line[2]['freight_value'] = 0.0
    #                 line[2]['other_value'] = 0.0
    #                 line[2]['insurance_value'] = 0.0
    #     return new_lines


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    # def write(self, values):
    #     result = super().write(values)
        # if 'freight_value' in values:
            # import pudb;pu.db
            # if values['freight_value'] == 0.0:
            # self.move_id._recompute_dynamic_lines(recompute_all_taxes=True)
            # print (values['invoice_line_ids'])
            # for line in values['invoice_line_ids']:
            #     print ('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
            #     print (line)
            # for line in values['invoice_line_ids']:
            #     print ('===============================================')
            #     # if len(line[2])
            #     print (line[2])
            # import pudb;pu.db
            # if self.amount_freight_value > 0.0:
            #     for line in values['invoice_line_ids']:
            #         line[2].update({'freight_value': 0.0})
            #     self._inverse_amount_freight()
            # for line in values['invoice_line_ids']:
            #     print ('===============================================')
            #     print (line[2])
                # print (values['invoice_line_ids'])
        # return result

#     # @api.onchange("quantity")
#     # def _onchange_quantity(self):
#     #     """To call the method in the mixin to update
#     #     the price and fiscal quantity."""
#     #     result = super()._onchange_quantity()

    @api.onchange('quantity', 'discount', 'price_unit', 'tax_ids')
    def _onchange_price_subtotal(self):
        result = super()._onchange_price_subtotal()
        self.move_id._recompute_dynamic_lines(recompute_all_taxes=True)
#         for line in self:
#             if line.freight_value:
#                 import pudb;pu.db
#                 if line.move_id.amount_freight_value:
#                     line.freight_value = 0.0
        return result
