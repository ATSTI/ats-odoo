from odoo import api, fields, models, _


class ResStateCity(models.Model):
    _inherit = 'res.state.city'
    
    ibge_code = fields.Char(string=u'IBGE Code', size=7, copy=False)
