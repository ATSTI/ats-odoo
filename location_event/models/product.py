# -*- coding: utf-8 -*-


from odoo import _, models,fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_location = fields.Boolean(string="Curso")