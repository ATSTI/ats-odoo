# -*- coding: utf-8 -*-

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class AccountMove(models.Model):
    _inherit = "account.move"

    commission_value = fields.Float('Comissão', digits=dp.get_precision('Account'),
                                readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})

    @api.onchange('commission_value')
    def _onchange_comission_value(self):
        for move in self:
            if move.commission_value:
                value = move.commission_value - move.amount_price_gross
                value_percent = (value * 100 / move.amount_price_gross) * -1
                for line in move.with_context(check_move_validity=False).line_ids:
                    # credito Venda de produtos
                    if line.account_id.user_type_id.internal_group == "income" and line.credit:
                        line.credit = move.commission_value
                    # Ipi credito
                    if line.account_id.user_type_id.internal_group == "liability" and line.credit:
                        line.credit = value * (-1)
                        line.ipi_percent = value_percent
                        line.ipi_value = value
                    # contrapartida do ipi Venda de produtos
                    if line.account_id.user_type_id.internal_group == "income" and line.debit:
                        line.debit = value * (-1)
                    # clientes a receber
                    if line.account_id.user_type_id.internal_group == "asset" and line.debit:
                        line.debit = move.commission_value

                move.update({
                    'amount_tax': value,
                })
                move.amount_total = move.amount_price_gross + move.amount_tax
                move.amount_financial_total = move.amount_price_gross + move.amount_tax
                move.amount_residual = move.amount_financial_total

    def button_dummy(self): 
        self._onchange_comission_value()
        return True
