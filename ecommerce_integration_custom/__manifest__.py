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
    'name': "Complementos de integração com E-Commerce's",
    'version': '1.0',
    'category': 'Others',
    'sequence': 2,
    'summary': 'Esse Modulo é um complementar para os modulos Shopee e Meli e suas respectivas Integrações. + Um relatório personalizado d elista de separação',
    'description': """
    """,
    'author': 'ATS Soluções',
    'maintainer': 'Mauricio Silveira, mauricio@atsti.com.br',
    'website': '',
    'depends': ['account', 'sale', 'shopee_odoo', 'meli_odoo'],
    'data': [
        'security/ir.model.access.csv',
        'report/report_separacao_felicita.xml',
        'views/sale_view.xml',
        'views/report_orcamento.xml',
        'wizard/importar_view.xml',
    ],
    'installable': True,
    'application': False,
}
