# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp

class SaleOrder(models.Model):
    _inherit = 'sale.order'

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

    def action_cancel(self):
        equip = self.env['partner.historico'].sudo().search([
            ('venda_id','=', self.id),
            ('partner_id','=', self.partner_id.id)
            ])
        if equip:
            equip.sudo().unlink()    
        return self.write({'state': 'cancel'})
