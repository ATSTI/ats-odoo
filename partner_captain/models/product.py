# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    historico_id = fields.Many2one(
        'crm.historico',
        string='Tipo Histórico CRM'
    )

    situacao = fields.Selection(
    [
        ('otima', 'Ótima'),
        ('bom', 'Bom'),
        ('medio', 'Médio'),
        ('ruim', 'Ruim'),
        ('pessimo', 'Péssimo'),
        ('manutencao', 'Manutenção')
    ],
    string="Situação",
    default='bom',
    tracking=True
)


    modelo = fields.Text("Modelo")

    tamanho_cd = fields.Selection(
        [
            ("jr", 'JR'),
            ('pp', 'PP'),
            ('p', 'P'),
            ('pl', 'PL'),
            ('m', 'M'),
            ('ml', 'ML'),
            ('g', 'G'),
            ('xl', 'XL'),
        ],
        string='Tamanho CD'
    )

    tag_cd = fields.Text("Tag CD")

    usado = fields.Boolean(
        "Produto está sendo usado?",
        default=False
    )

    tipo_suit = fields.Selection(
        [
            ('fina_piscina', 'FINA PISCINA'),
            ('grossa', 'GROSSA'),
            ('fina_mar', 'FINA MAR')
        ],
        string='Tipo de SUIT'
    )

    is_suit = fields.Boolean(compute="_compute_is_suit", store=False)


    tipo_reg = fields.Selection(
        [
            ('balanceado', 'BALANCEADO'),
            ('console_duplo', 'NÃO BALANCEADO/CONSOLE DUPLO'),
            ('nao_balanceado', 'NÃO BALANCEADO'),

        ],
        string='Tipo de REG'
    )

    is_reg = fields.Boolean(compute="_compute_is_reg", store=False)




    @api.depends('categ_id')
    def _compute_is_suit(self):
        Category = self.env['product.category']
        suit_category = Category.search([('name', '=', 'SUIT')], limit=1)

        for rec in self:
            rec.is_suit = bool(suit_category and rec.categ_id == suit_category)

    
    @api.depends('categ_id')
    def _compute_is_reg(self):
        Category = self.env['product.category']
        reg_category = Category.search([('name', '=', 'Reguladores')], limit=1)
        for rec in self:
            rec.is_reg = bool(reg_category and rec.categ_id == reg_category)