from odoo import models, fields
from .cst import ORIGEM_PROD


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    fiscal_type_bkp = fields.Selection(
        [('service', u'Serviço'), ('product', 'Produto')], 'Tipo Fiscal',
        )
    origin_bkp = fields.Selection(ORIGEM_PROD, 'Origem', default='0')
    ncm = fields.Char(string="NCM", size=14)
    code_servico = fields.Char(u'Código Serviço', size=16)
