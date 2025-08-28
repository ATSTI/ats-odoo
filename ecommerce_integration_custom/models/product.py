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

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, date, timedelta

class ProductTemplate(models.Model):

    _inherit = 'product.template'

    def rotina_atualiza_preco_online(self):
        hj = datetime.now()
        hj = hj - timedelta(hours=12)
        hj = datetime.strftime(hj,'%Y-%m-%d %H:%M:%S')
        lines = self.env['auditlog.log.line'].search([
            ('log_id.create_date', '>=', hj),
            ('log_id.model_id.model', '=', 'product.template'),
            ('field_name', 'in', ['price_shopee', 'price_meli']),
            ('new_value_text', '!=', False),
        ])

        for line in lines:
            product = self.env['product.template'].browse(line.log_id.res_id)
            if not product:
                continue

            if line.field_name == 'price_shopee' and product.shopee:
                print("PRODUTO SERIA ATUALIZADO SHOPEE - ", product.name)
                product.atualiza_preco_shopee()

            elif line.field_name == 'price_meli' and product.meli:
                print("PRODUTO SERIA ATUALIZADO MELI - ", product.name)
                product.action_envia_produto_meli()
