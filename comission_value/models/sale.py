# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Faslu Rahman(odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # @api.depends('order_line.price_total')
    # def _amount_all(self):
    #     """
    #     Compute the total amounts of the SO.
    #     """
    #     res = super()._compute_amount()
    #     """
    #     for order in self:
    #         amount_discount = 0.0
    #         for line in order.order_line:
    #             # amount_untaxed += line.price_subtotal
    #             # amount_tax += line.price_tax
    #             amount_discount += (line.product_uom_qty * line.price_unit * line.discount) / 100
    #         order.update({
    #             # 'amount_untaxed': amount_untaxed,
    #             # 'amount_tax': amount_tax,
    #             'amount_discount': amount_discount,
    #             # 'amount_total': amount_untaxed + amount_tax,
    #         })
    #     """
    #     return res

    commission_value = fields.Float('Comissão', digits=dp.get_precision('Account'),
                                readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})

    @api.onchange('commission_value')
    def _onchange_comission_value(self):
        import pudb;pu.db
        for order in self:
            if order.commission_value:
                value = order.commission_value - order.amount_price_gross
                value_percent = (value * 100 / order.amount_price_gross) * -1
                # self.amount_tax = value
                order.update({
                    'amount_tax': value,
                })
                for line in order.order_line:
                    line.ipi_percent = value_percent
                    line.ipi_value = value
                order.amount_total = order.amount_price_gross + order.amount_tax
                order.amount_financial_total = order.amount_price_gross + order.amount_tax
                # order._amount_all()

    def _prepare_invoice(self, ):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals.update({
            'commission_value': self.commission_value
        })
        return invoice_vals
    
    def _create_invoices(self, grouped=False, final=False, date=None):
        invoice = super()._create_invoices(grouped=grouped, final=final, date=date)
        invoice._onchange_comission_value()
        return invoice

    def button_dummy(self): 
        self._onchange_comission_value()
        return True
        


# class SaleOrderLine(models.Model):
#     _inherit = "sale.order.line"

#     discount_type = fields.Selection([('percent', 'Percentagem'), ('amount', 'Valor')], string='Tipo desconto',
#                                      readonly=True,
#                                      states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
#                                      default='percent')
#     discount_rate_t = fields.Float('Desconto', digits=dp.get_precision('Account'),
#                                  readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    
#     # discount = fields.Float(string='Discount (%)', digits=(16, 20), default=0.0)

#     def _prepare_invoice_line(self, **optional_values):
#         self.ensure_one()
#         invoice_line_vals = super()._prepare_invoice_line(**optional_values)
#         if self.discount_value:
#             # discount = (
#             #             (self.product_uom_qty * self.price_unit) * (self.discount / 100.0)
#             #         )
#             invoice_line_vals.update({
#                 'discount_value': self.discount_value,
#                 'discount': self.discount
#             })
#         return invoice_line_vals

#     def button_update_discount(self):
#         for line in self:
#             if line.discount_type == 'percent':
#                 line.discount_fixed = True
#                 line.discount_fixed = True
#                 # order.discount_rate = order.discount_rate_t
#                 # for line in order.order_line:
#                 #     line.discount_value = (line.product_uom_qty * line.price_unit * order.discount_rate_t) / 100                
#                 if line.discount_rate_t:
#                     line.discount = line.discount_rate_t
#                     line.discount_value = (line.discount_rate_t / 100) * (
#                         line.product_uom_qty * line.price_unit or 1
#                     )
#                 else:
#                     line.discount_value = 0.0
#             else:
#                 line.discount_fixed = True
#                 if line.discount_rate_t:
#                     line.discount_fixed = True
#                     line.discount_value = line.discount_rate_t
#                     line.discount = (line.discount_rate_t * 100) / (
#                         line.product_uom_qty * line.price_unit or 1
#                     )
#                 else:
#                     line.discount = 0.0
