# -*- encoding: utf-8 -*-

from odoo import fields,models,api, _


class ProductTemplate (models.Model):
    _inherit = 'product.template'

    # margin = fields.Integer(string="Margem (%)")
    qtde_atacado = fields.Integer(string="Qtde. Atacado")
    preco_atacado = fields.Float(string="Preço Atacado")
    tipo_venda = fields.Selection([
        ('1', '1 - Normal'),
        ('2', '2 - Venda Extra'),
        ('3', '3 - Melhor Beneficio'),
        ('4', '4 - Atacado'),
        ('5', '5 - Curso'),
        ('6', '6 - Outros'),
        ('7', '7 - Quinta-feira do Chocolate'),
        ], 'Tipo de Venda', default='1')
    image_promocao_512 = fields.Image("Promoção (*.jpg)", max_width=512, max_height=512, store=True)
