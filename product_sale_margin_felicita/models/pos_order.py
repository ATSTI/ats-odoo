# -*- encoding: utf-8 -*-

from odoo import fields,models,api, _


class PosOrderLine (models.Model):
    _inherit = 'pos.order.line'

    tipo_venda = fields.Selection([
        ('1', '1 - Normal'),
        ('2', '2 - Venda Extra'),
        ('3', '3 - Melhor Beneficio'),
        ('4', '4 - Atacado'),
        ('5', '5 - Curso'),
        ('6', '6 - Outros'),
        ('7', '7 - Quinta-feira do Chocolate'),
        ], 'Tipo de Venda', default='1')