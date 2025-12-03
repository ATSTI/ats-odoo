# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2011 Camptocamp SA (http://www.camptocamp.com)
#    All Right Reserved
#
#    Author : Joel Grand-Guillaume (Camptocamp)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, models, _
from odoo.exceptions import UserError

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _reach_floor_price(self, floor_price, discount, price_unit):
        sell_price = price_unit * (1 - (discount or 0.0) / 100.0)
        precision =  self.env['decimal.precision'].precision_get('Sale Price')
        sell_price = round(sell_price, precision)
        if (sell_price < floor_price):
            return True
        return False

    def _compute_lowest_discount(self, desconto, price_list):
        disc = desconto * price_list
        return abs(round(disc*100, 2))

    def _compute_lowest_price(self, floor_price, discount):
        if discount == 100.0:
            res = 0.0
        else:
            res = floor_price / (1-(discount / 100.0))
        return res

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        '''
        Overload method:
            - Empty the discount when changing.
        '''
        res = super(SaleOrderLine, self).product_id_change()
        if 'discount' in res:
            res['discount'] = 0.0
        return res

    @api.onchange(
        'product_id', 'price_unit', 'product_uom',
        'product_uom_qty', 'tax_id', 'discount'
    )
    def _onchange_discount(self):
        res = {}
        warning_msgs = []

        for line in self:
            if not line.product_id or not line.price_unit:
                continue

            partner = line.order_id.partner_id
            price_list = line.product_id.list_price

            # =========================
            # 1) TETO DE DESCONTO (SE EXISTIR)
            # =========================
            if partner.roof_discount_limit and price_list > 0:
                desconto = (1 - (line.price_unit / price_list)) * 100

                if desconto > partner.roof_discount_limit:
                    warning_msgs.append(_(
                        "O desconto de %.2f%% excede o limite máximo de %.2f%% para este parceiro."
                    ) % (desconto, partner.roof_discount_limit))
                    res['warning'] = {
                        'title': _('Desconto inválido!'),
                        'message': '\n'.join(warning_msgs),
                    }
                    line.price_unit = price_list - (partner.roof_discount_limit/100 * price_list)
            # =========================
            # 2) PISO DE PREÇO (SÓ SE NÃO TIVER TETO)
            # =========================
            if not partner.roof_discount_limit:
                floor_price = line.product_id.floor_price_limit
                if floor_price and line.price_unit < floor_price:
                    warning_msgs.append(_(
                        "O preço R$%.2f é menor do que o mínimo permitido de R$%.2f."
                    ) % (line.price_unit, floor_price))
                    res['warning'] = {
                        'title': _('Preço inválido!'),
                        'message': '\n'.join(warning_msgs),
                    }
                    line.price_unit = floor_price

        return res