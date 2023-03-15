# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_confirm(self):
        result = super(SaleOrder, self).action_confirm()
        if self.order_line:
            for line in self.order_line:
                if line.product_id.historico_id: 
                    if line.product_id.historico_id.tipo in ('c','e','v'):
                        for equip in self.partner_id.historico_line:
                            if equip.id == line.product_id.historico_id.id:
                                continue
                        # grava no cadastro do cliente                       
                        hist = {}
                        hist['venda_id'] = self.id
                        hist['partner_id'] = self.partner_id.id
                        hist['historico_id'] = [(6, 0, {line.product_id.historico_id.id})]
                        self.env['partner.historico'].sudo().create(hist)
        return result

    @api.multi
    def action_cancel(self):
        equip = self.env['partner.historico'].sudo().search([
            ('venda_id','=', self.id),
            ('partner_id','=', self.partner_id.id)
            ])
        if equip:
            equip.sudo().unlink()    
        return self.write({'state': 'cancel'})
