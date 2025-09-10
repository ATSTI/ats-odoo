from odoo import models, fields

class ProductProduct(models.Model):
    _inherit = 'product.product'

    picking_id = fields.One2many('stock.picking', 'sale_id', string='Transfers')

    #kit = fields.Boolean('KIT')