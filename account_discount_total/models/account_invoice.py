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


class AccountMove(models.Model):
    _inherit = "account.move"

    discount_type = fields.Selection([('percent', 'Percentagem'), ('amount', 'Valor')], string='Tipo desconto',
                                     readonly=True, states={'draft': [('readonly', False)]}, default='percent')
    discount_rate = fields.Float('Total desconto', digits=(16, 2), readonly=True,
                                 states={'draft': [('readonly', False)]})
    amount_discount = fields.Monetary(string='Desconto', store=True, readonly=True, compute='_compute_amount',
                                      track_visibility='always')

    def ajusta_valores(self):
        for move in self:
            if move.amount_untaxed and move.invoice_line_ids:
                total = 0.0
                for line in move.invoice_line_ids:
                    total += (line.quantity * line.price_unit)
                move.amount_discount_value = move.discount_rate
                move.amount_total = total - move.amount_discount_value
                move.amount_untaxed = total

    @api.onchange('discount_type', 'discount_rate', 'invoice_line_ids')
    def supply_rate(self):
        for inv in self:
            total = discount = 0.0
            for line in inv.invoice_line_ids:
                total += (line.quantity * line.price_unit)
            self.discount_rate = self.discount_rate
            if inv.discount_type == 'percent':
                for line in inv.invoice_line_ids:
                    price_unit_discount = (
                        line.price_unit * line.quantity * (inv.discount_rate / 100.0)
                    )                    
                    line.discount_value = price_unit_discount
                    line._onchange_price_subtotal()
            else:
                if inv.discount_rate != 0:
                    discount = (inv.discount_rate / total) * 100
                else:
                    discount = inv.discount_rate
                for line in inv.invoice_line_ids:
                    price_unit_discount = (
                        line.price_unit * line.quantity * (discount / 100.0)
                    )
                    line.discount_value = price_unit_discount
                    line._onchange_price_subtotal()
            inv._move_autocomplete_invoice_lines_values()
            inv.amount_untaxed = total

    def button_dummy(self):
        self.supply_rate()
        return True

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.model_create_multi
    def create(self, vals_list):
        result = super(
                    AccountMoveLine, self.with_context(create_from_move_line=True)
                ).create(vals_list)
        for values in vals_list:
            for line in result:
                if line.product_id.id == values.get("product_id") and line.price_total == values.get("price_total"):
                    discount = values.get("discount")
                    if discount and values.get("discount_value") and not line.discount_value:
                        price_unit_discount = (
                            (values.get("price_unit") * values.get("quantity")) * (discount / 100.0)
                        )
                        line.update({"discount_value": price_unit_discount})
        return result