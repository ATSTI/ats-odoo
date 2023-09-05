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
    'name': 'Relatorios Orcamento',
    'version': '1.0',
    'category': 'Others',
    'sequence': 2,
    'summary': 'relatorios personalizados',
    'description': """
    """,
    'author': 'ATS Soluções',
    'website': '',
    'depends': ['account', 'sale', 'mrp', 'report_cabecalho'],
    'data': [
        'report/report_entregadevolucao_locefaca.xml',
        'report/report_servico_locefaca.xml',
        'report/report_locacao_locefaca.xml',
        'report/report_instalacao_locefaca.xml',
        'report/report_venda_locefaca.xml',
        'views/report_orcamento.xml',
        'views/sale_order_view.xml',
    ],
    'installable': True,
    'application': False,
}
