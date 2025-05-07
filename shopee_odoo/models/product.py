# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import date


class ProducTemplate(models.Model):
    _inherit = "product.template"

    shopee = fields.Boolean(
        string='Vende Shopee?',
        default=False,
        )
    shopee_item_id = fields.Char('Id do Item')
    margin_shopee = fields.Float(u'Margin')