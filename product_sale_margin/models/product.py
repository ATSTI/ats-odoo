# -*- encoding: utf-8 -*-

from odoo import fields,models,api, _

class ProductProduct (models.Model):
    _inherit = 'product.product'

    margin = fields.Integer(string="Margem (%)")
    qtde_atacado = fields.Integer(string="Qtde. Atacado")
    preco_atacado = fields.Float(string="Preço Atacado")

    #@api.onchange('margin')
    #def onchange_margin(self):
    #    if self.margin:
    #        self.list_price = self.standard_price * (1 + (float(self.margin)/100))


class ProductTemplate (models.Model):
    _inherit = 'product.template'

    margin = fields.Integer(related='product_variant_ids.margin')
    qtde_atacado = fields.Integer(related='product_variant_ids.qtde_atacado')
    preco_atacado = fields.Float(related='product_variant_ids.preco_atacado')
    tipo_venda = fields.Selection([
        ('1', '1 - Normal'),
        ('2', '2 - Venda Extra'),
        ('3', '3 - Melhor Beneficio'),
        ('4', '4 - Atacado'),
        ('5', '5 - Curso'),
        ('6', '6 - Outros'),
        ], 'Tipo de Venda', default='1')


    @api.onchange('margin')
    def onchange_margin(self):
        if self.margin:
            self.list_price = self.standard_price * (1 + (float(self.margin)/100))

    @api.multi
    def write(self, vals):
        if 'list_price' in vals:
            if self.standard_price:
                vals['margin'] = round(((vals['list_price'] / self.standard_price) - 1),2) * 100
            if 'standard_price' in vals:
                vals['margin'] = round(((vals['list_price'] / vals['standard_price']) - 1),2) * 100
        return super(ProductTemplate, self).write(vals)
 
