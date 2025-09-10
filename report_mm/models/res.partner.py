from odoo import models,fields



class Partner(models.Model):
    _inherit = 'res.partner'

    contact_ids = fields.One2many('res.partner', 'parent_id', string='Contatos')

