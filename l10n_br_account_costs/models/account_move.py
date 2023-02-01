# Copyright (C) 2009  Renato Lima - Akretion
# Copyright (C) 2012  Raphaël Valyi - Akretion
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from functools import partial

from odoo import api, fields, models
from odoo.tools import float_is_zero
from odoo.tools.misc import formatLang
from collections import defaultdict

from ...l10n_br_fiscal.constants.fiscal import (
    CFOP_DESTINATION_EXPORT,
    FISCAL_IN
)


# class AccountMove(models.Model):
#     _inherit = "account.move"
class AccountMove(models.Model):
    _name = "account.move"
    _inherit = [
        _name,
        "l10n_br_fiscal.document.mixin.methods",
        "l10n_br_fiscal.document.invoice.mixin",
    ]
    _inherits = {"l10n_br_fiscal.document": "fiscal_document_id"}
    _order = "date DESC, name DESC"
    
    amount_freight_value = fields.Monetary(
        inverse="_inverse_amount_freight",
    )
    
    amount_insurance_value = fields.Monetary(
        inverse="_inverse_amount_insurance",
    )

    amount_other_value = fields.Monetary(
        inverse="_inverse_amount_other",
    )

    @api.depends('amount_freight_value')
    def _inverse_amount_freight(self):
        super()._inverse_amount_freight()
        if len(self) > 1:
            return
        for move in self:
            if move.payment_state == 'invoicing_legacy':
                move.payment_state = move.payment_state
                continue
            # se ja existe tem q excluir
            for line in move.line_ids:
                if line.name in ["[FREIGHT]"]:
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
                if not line.exclude_from_invoice_tab and line.freight_value > 0:
                    new_line = self.env["account.move.line"].new(
                            {
                                "name": "[FREIGHT]",
                                "account_id": line.account_id.id,
                                "move_id": self.id,
                                "exclude_from_invoice_tab": True,
                                "price_unit": line.freight_value,
                            }
                    )
                    move.line_ids += new_line
                    move.with_context(check_move_validity=False)._onchange_currency()

    @api.depends('amount_other_value')
    def _inverse_amount_other(self):
        super()._inverse_amount_other()
        if len(self) > 1:
            return
        for move in self:
            if move.payment_state == 'invoicing_legacy':
                move.payment_state = move.payment_state
                continue
            # se ja existe tem q excluir
            for line in move.line_ids:
                if line.name in ["[OTHER]"]:
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
                if not line.exclude_from_invoice_tab and line.other_value > 0:
                    if line.other_value:
                        new_line = self.env["account.move.line"].new(
                            {
                                "name": "[OTHER]",
                                "account_id": line.account_id.id,
                                "move_id": self.id,
                                "exclude_from_invoice_tab": True,
                                "price_unit": line.other_value,
                            }
                        )
                    move.line_ids += new_line
                    move.with_context(check_move_validity=False)._onchange_currency()

    @api.depends('amount_insurance_value')
    def _inverse_amount_insurance(self):
        super()._inverse_amount_insurance()
        if len(self) > 1:
            return
        for move in self:
            if move.payment_state == 'invoicing_legacy':
                move.payment_state = move.payment_state
                continue
            # se ja existe tem q excluir
            for line in move.line_ids:
                if line.name in ["[INSURANCE]"]:
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
                if not line.exclude_from_invoice_tab and line.insurance_value > 0:
                    if line.insurance_value:
                        new_line = self.env["account.move.line"].new(
                            {
                                "name": "[INSURANCE]",
                                "account_id": line.account_id.id,
                                "move_id": self.id,
                                "exclude_from_invoice_tab": True,
                                "price_unit": line.insurance_value,
                            }
                        )
                    move.line_ids += new_line
                    move.with_context(check_move_validity=False)._onchange_currency()

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
        'line_ids.other_value',)
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
            currencies = move._get_lines_onchange_currency().currency_id
            
            for line in move.line_ids:
                if move.is_invoice(include_receipts=True):
                    
                    total_other += line.freight_value + line.insurance_value + line.other_value
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
                            total += total_other
                            total_currency += total_other
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