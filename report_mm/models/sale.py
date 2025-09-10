from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    contact_id = fields.Many2one('res.partner', 'Contato', domain="[('parent_id', '=', partner_id)]" )