# -*- coding: utf-8 -*-
# © 2017  Carlos R. Silveira
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    item_id = fields.Char(related='product_variant_ids.item_id', readonly=False)
    variant_id = fields.Char(related='product_variant_ids.variant_id', readonly=False) 
    #online_venda = fields.Boolean(related='product_variant_ids.online_venda')
    #online_preco = fields.Float(related='product_variant_ids.online_preco')
    #online_estoque = fields.Float(related='product_variant_ids.online_estoque')
    online_venda = fields.Boolean(string='Vende Online?')
    online_preco = fields.Float(related='product_variant_ids.online_preco', readonly=False)
    online_estoque = fields.Float(related='product_variant_ids.online_estoque', readonly=False)
    altura = fields.Char(string='Altura')
    comprimento = fields.Char(string='Comprimento')
    largura = fields.Char(string='Largura')
    peso = fields.Char(string='Peso')

    
class ProductProduct(models.Model):
    _inherit = 'product.product'  
    
    item_id = fields.Char(string='Id. Item Ext.')
    variant_id = fields.Char(string='Id. Variant Ext.') 
    online_preco = fields.Float(string='Preço Online')
    online_estoque = fields.Float(string='Estoque Online')
  
