# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-Today OpenERP S.A. (<http://www.openerp.com>).
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

{
    'name': 'Criação de projeto do pedido de venda (produto)',
    'version': '1.0',
    'category': 'Others',
    'sequence': 2,
    'summary': 'cria um projeto a partir de um pedido de venda que seja produto',
    'description': """
    """,
    'author': 'ATS Soluções',
    'website': '',
    'depends': ['sale', 'sale_stock', 'sale_mrp', 'sale_project', 'sale_project_service_tracking_copy_tasks', 'project', 'account'],
    'data': [
        'views/sale_view.xml',
        'views/account_view.xml',
        'views/stock_view.xml',
    ],
    'installable': True,
    'application': False,
}
