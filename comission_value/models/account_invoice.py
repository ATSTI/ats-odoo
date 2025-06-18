# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    commission_value = fields.Float('Comissão', digits=dp.get_precision('Account'),
                                readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    amount_other_value = fields.Monetary("Outros valores")

    #@api.onchange('commission_value')
    def _comission_value(self):
        for move in self:
            if move.commission_value:
                value = move.commission_value - move.amount_untaxed
                # value_percent = (value * 100 / move.amount_untaxed) * -1
                value_comission = move.commission_value / len(move.invoice_line_ids)
                comission_total = move.commission_value
                total_itens = 0
                for line in move.with_context(check_move_validity=False).line_ids:
                    # credito Venda de produtos
                    if line.account_id.user_type_id.internal_group == "income" and line.credit:
                        total_itens += 1
                        if total_itens == len(move.invoice_line_ids):
                            line.credit = round(comission_total, 2)                            
                        else:
                            line.credit = round(value_comission, 2)
                        comission_total -= round(value_comission, 2)
                    # Ipi credito
                    if line.account_id.user_type_id.internal_group == "liability" and line.credit:
                        line.credit = value * (-1)
                    # contrapartida do ipi Venda de produtos
                    if line.account_id.user_type_id.internal_group == "income" and line.debit:
                        line.debit = value * (-1)
                    # clientes a receber
                    if line.account_id.user_type_id.internal_group == "asset" and line.debit:
                        line.debit = move.commission_value
                        

                move.write({
                    'amount_other_value': value * -1 ,
                })
                move.amount_total = move.commission_value
                move.amount_financial_total = move.commission_value
                move.amount_residual = move.amount_financial_total

    def button_dummy(self): 
        return self._comission_value()