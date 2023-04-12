# -*- encoding: utf-8 -*-

from odoo import fields,models,api, _

class ProductProduct (models.Model):
    _inherit = 'product.product'

    margin = fields.Integer(string="Margem (%)")

    @api.onchange('margin')
    def onchange_margin(self):
        if self.margin:
            #self.lst_price = self.standard_price * (1 + (float(self.margin)/100))
            self.list_price = self.standard_price * (1 + (float(self.margin)/100))

class ProductTemplate (models.Model):
    _inherit = 'product.template'

    margin = fields.Integer(related='product_variant_ids.margin')

    @api.onchange('margin')
    def onchange_margin(self):
        if self.margin:
            #self.lst_price = self.standard_price * (1 + (float(self.margin)/100))
            self.list_price = self.standard_price * (1 + (float(self.margin)/100))
