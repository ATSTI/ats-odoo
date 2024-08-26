# -*- encoding: utf-8 -*-

from odoo import fields,models,api, _


class ProductTemplate (models.Model):
    _inherit = 'product.template'

    margin = fields.Integer(string="Margem (%)")

    @api.onchange('margin')
    def onchange_margin(self):
        if self.margin:
            self.list_price = self.standard_price * (1 + (float(self.margin)/100))

    def write(self, vals):
        if 'list_price' in vals:
            if self.standard_price:
                vals['margin'] = round(((vals['list_price'] / self.standard_price) - 1),2) * 100
            if 'standard_price' in vals:
                vals['margin'] = round(((vals['list_price'] / vals['standard_price']) - 1),2) * 100
        return super(ProductTemplate, self).write(vals)
