# -*- coding: utf-8 -*-
# Copyright 2004-2010 OpenERP SA
# Copyright 2017 RGB Consulting S.L. (https://www.rgbconsulting.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class LoyaltyRule(models.Model):
    _name = 'loyalty.rule'

    name = fields.Char(string='Regra', size=32, index=True, required=True)
    type = fields.Selection(selection=[('product', 'Produto'),
                                       ('category', 'Categoria')],
                            string='Tipo', required=True, default='product',
                            help='The concept this rule applies to')
    cumulative = fields.Boolean(string='Acumulativo', help='The points from this rule will be added '
                                     'to points won from other rules with '
                                     'the same concept')
    pp_product = fields.Float(string='Pontos por produto',
                              help='Amount of points earned per product')
    pp_currency = fields.Float(string='Pontos por valor',
                               help='Amount of points earned per currency')
    loyalty_program_id = fields.Many2one(comodel_name='loyalty.program',
                                         string='Promoção',
                                         help='The Loyalty Program this rule '
                                              'belongs to')
    product_id = fields.Many2one(comodel_name='product.product',
                                 string='Produto da Promoção',
                                 help='The product affected by this rule')
    category_id = fields.Many2one(comodel_name='pos.category',
                                  string='Categoria da Promoção',
                                  help='The category affected by this rule')
