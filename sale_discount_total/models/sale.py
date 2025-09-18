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

    discount_type = fields.Selection([('percent', 'Percentagem'), ('amount', 'Valor')], string='Tipo desconto',
                                     readonly=True,
                                     states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
                                     default='percent')
    discount_rate_t = fields.Float('Desconto', digits=dp.get_precision('Account'),
                                 readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})

    @api.onchange('discount_type', 'discount_rate_t', 'order_line')
    def supply_rate(self):
        for order in self:
            if order.discount_type == 'percent':
                order.discount_rate = order.discount_rate_t
                for line in order.order_line:
                    line.discount_value = (line.product_uom_qty * line.price_unit * order.discount_rate_t) / 100
            else:
                total = discount = 0.0
                for line in order.order_line:
                    total += round((line.product_uom_qty * line.price_unit))
                if order.discount_rate_t != 0:
                    discount = (order.discount_rate_t / total) * 100
                else:
                    discount = order.discount_rate_t
                order.discount_rate = discount
                for line in order.order_line:                
                    line.discount_value = (line.product_uom_qty * line.price_unit * discount) / 100
                

    def _prepare_invoice(self, ):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals.update({
            'discount_type': self.discount_type,
            'discount_rate': self.discount_rate_t,
        })
        return invoice_vals

    def button_dummy(self):
        self.supply_rate()
        # self._amount_all()
        return True


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    discount_type = fields.Selection([('percent', 'Percentagem'), ('amount', 'Valor')], string='Tipo desconto',
                                     readonly=True,
                                     states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
                                     default='percent')
    discount_rate_t = fields.Float('Desconto', digits=dp.get_precision('Account'),
                                 readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})

    def _prepare_invoice_line(self, **optional_values):
        self.ensure_one()
        invoice_line_vals = super()._prepare_invoice_line(**optional_values)
        if self.discount_value:
            invoice_line_vals.update({
                'discount_value': self.discount_value,
                'discount': self.discount
            })
        return invoice_line_vals

    def button_update_discount(self):
        for line in self:
            if line.discount_type == 'percent':
                line.discount_fixed = True
                line.discount_fixed = True
                if line.discount_rate_t:
                    line.discount = line.discount_rate_t
                    line.discount_value = (line.discount_rate_t / 100) * (
                        line.product_uom_qty * line.price_unit or 1
                    )
                else:
                    line.discount_value = 0.0
            else:
                line.discount_fixed = True
                if line.discount_rate_t:
                    line.discount_fixed = True
                    line.discount_value = line.discount_rate_t
                    line.discount = (line.discount_rate_t * 100) / (
                        line.product_uom_qty * line.price_unit or 1
                    )
                else:
                    line.discount = 0.0