# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class ProductCategoryChange(models.TransientModel):
    """ Permite criar o Certificado para os inscritos """
    _name = 'product.category.change'
    _description = 'Trocaar categorias dos produtos'

    categoria = fields.Many2one('product.category', required="true")

    def action_trocar_categoria(self):
        prd_ids = self.env['product.template'].browse(self._context.get('active_ids', []))
        if self.categoria:       
            for prd in prd_ids:
                prd.categ_id = self.categoria.id
