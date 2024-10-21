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

    @api.depends('order_line.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        res = super()._compute_amount()
        for order in self:
            amount_discount = 0.0
            for line in order.order_line:
                # amount_untaxed += line.price_subtotal
                # amount_tax += line.price_tax
                amount_discount += (line.product_uom_qty * line.price_unit * line.discount) / 100
            order.update({
                # 'amount_untaxed': amount_untaxed,
                # 'amount_tax': amount_tax,
                'amount_discount': amount_discount,
                # 'amount_total': amount_untaxed + amount_tax,
            })
        return res

    discount_type = fields.Selection([('percent', 'Percentagem'), ('amount', 'Valor')], string='Tipo desconto',
                                     readonly=True,
                                     states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
                                     default='percent')
    discount_rate_t = fields.Float('Desconto', digits=dp.get_precision('Account'),
                                 readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    # amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all',
    #                                  track_visibility='always')
    # amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all',
    #                              track_visibility='always')
    # amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all',
    #                                track_visibility='always')
    amount_discount = fields.Monetary(string='Total desconto', store=True, readonly=True, compute='_amount_all',
                                      digits=dp.get_precision('Account'), track_visibility='always')

    @api.onchange('discount_type', 'discount_rate_t', 'order_line')
    def supply_rate(self):

        for order in self:
            if order.discount_type == 'percent':
                order.discount_rate = order.discount_rate_t
                # for line in order.order_line:
                    # line.discount = order.discount_rate_t
            else:
                total = discount = 0.0
                for line in order.order_line:
                    total += round((line.product_uom_qty * line.price_unit))
                if order.discount_rate_t != 0:
                    discount = (order.discount_rate_t / total) * 100
                else:
                    discount = order.discount_rate_t
                # for line in order.order_line:
                    # line.discount = discount
                order.discount_rate = discount
                

    def _prepare_invoice(self, ):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals.update({
            'discount_type': self.discount_type,
            'discount_rate': self.discount_rate_t,
        })
        return invoice_vals

    def button_dummy(self):

        self.supply_rate()
        return True


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    # discount = fields.Float(string='Discount (%)', digits=(16, 20), default=0.0)

    def _prepare_invoice_line(self, **optional_values):
        self.ensure_one()
        invoice_line_vals = super()._prepare_invoice_line(**optional_values)
        if self.discount:
            discount = (
                        (self.product_uom_qty * self.price_unit) * (self.discount / 100.0)
                    )
            invoice_line_vals.update({
                'discount_value': discount
            })
        return invoice_line_vals
