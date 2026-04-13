# -*- coding: utf-8 -*-

from odoo import api, fields, models,_

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    #@api.depends('purchase_itens_ref')
    #def _compute_update_price(self):
    #    for order in self:
    #        order.update_price_count = len(self.purchase_itens_ref)
        

    purchase_itens_ref = fields.Many2one('purchase.itens',string="Itens do produto")
    #update_price_count = fields.Integer(compute='_compute_update_price', string='Definir Preços', default=0)
    #update_price_count = fields.Integer(string='Definir Preços', default=)

    def button_confirm(self):
        vals = {}
        vals['purchase_order_ref'] = self.name
        itens_list = []
        for l in self.order_line:
            itens_list.append((0,0,{
                'name' : l.product_id.name,
                'product_id' : l.product_id.id,
                'product_cst' : l.price_unit,
                'price' : l.product_id.list_price,
                'margin' : l.product_id.margin,
                'new_price' : 0.0,
                'new_margin' : 0
            }))
        vals['purchase_lines'] = itens_list
        self.purchase_itens_ref = self.env['purchase.itens'].create(vals).id
        super(PurchaseOrder, self).button_confirm()

    def abrir_item_pedidos(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Itens da compra',
            'res_model': 'purchase.itens',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', [self.purchase_itens_ref.id])],
            'context': {},
        }
