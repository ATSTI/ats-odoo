# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    commission_value = fields.Float('Comissão', digits=dp.get_precision('Account'),
                                readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    commission = fields.Boolean('Comissão', invisible=True)

    @api.onchange('commission_value')
    def _onchange_comission_value(self):        
        for move in self:
            if move.commission_value:
                if move.commission == False:
                    move.commission = True
                    return {
                        'warning': {
                            'title': "Aviso",
                            'message': "Insira Novamente o Valor da Comissão",
                        }
                    }
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
                        # line.ipi_percent = value_percent
                        # line.ipi_value = value
                    # contrapartida do ipi Venda de produtos
                    if line.account_id.user_type_id.internal_group == "income" and line.debit:
                        line.debit = value * (-1)
                    # clientes a receber
                    if line.account_id.user_type_id.internal_group == "asset" and line.debit:
                        line.debit = move.commission_value
                        

                move.amount_other_value = value * -1
                move.amount_total = move.commission_value
                move.amount_financial_total = move.commission_value
                move.amount_residual = move.amount_financial_total

    def button_dummy(self): 
        self._onchange_comission_value()
        return True
    
    # def action_post(self):
    #     value = self.commission_value - self.amount_untaxed
    #     res = super().action_post()
    #     self.amount_tax = value
    #     return res
        


# class AccountMoveLine(models.Model):
#     _name = "account.move.line"
#     _inherit = [_name, "l10n_br_fiscal.document.line.mixin.methods"]

#     def _prepare_fields_ipi(self, tax_dict):
#         self.ensure_one()
#         cst_id = tax_dict.get("cst_id").id if tax_dict.get("cst_id") else False
#         if self.move_id.commission_value:
#             percent = (self.move_id.commission_value - self.move_id.amount_untaxed) / self.move_id.amount_untaxed
#             ipi_value = percent * self.price_subtotal
#         else:
#             ipi_value = tax_dict.get("tax_value", 0.00)
#         return {
#             "ipi_cst_id": cst_id,
#             "ipi_base_type": tax_dict.get("base_type", False),
#             "ipi_base": tax_dict.get("base", 0.00),
#             "ipi_percent": tax_dict.get("percent_amount", 0.00),
#             "ipi_reduction": tax_dict.get("percent_reduction", 0.00),
#             "ipi_value": ipi_value,
#         }
