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
        import pudb;pu.db
        hj = datetime.now()
        hj = hj - timedelta(hours=12)
        hj = datetime.strftime(hj,'%Y-%m-%d %H:%M:%S')
        audit = self.env['auditlog.log'].search([
            ('create_date', '>=', hj),
            ('model_id', '=', 'product.template'),
        ])
        prod_ids = []
        for pr in audit:
            for line in pr.line_ids:
                if line.field_name in (
                    'standard_price'
                ):
                    import pudb;pu.db
                    prod_ids = self.env['product.template'].browse([pr.res_id])
                    if prod_ids and prod_ids.shopee:
                        prod_ids.atualiza_preco_shopee()
                    if prod_ids and prod_ids.meli:
                        prod_ids.action_envia_produto_meli()
