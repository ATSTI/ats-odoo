from odoo import fields, api, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    moeda_cotacao = fields.Selection([
        ('USD', 'Dólar'),
        ('BRL','Real')
    ], string=' Moeda da cotação', default='USD')   