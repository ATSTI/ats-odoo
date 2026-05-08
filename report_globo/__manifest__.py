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
    'name': 'Relatório para Globo verduras',
    'version': '14.0',
    'category': 'Others',
    'sequence': 2,
    'summary': 'Impressão de um relatório específico para a empresa Globo verduras',
    'description': """ Relatório para Globo verduras, desenvolvido para atender as necessidades específicas da empresa, proporcionando uma visualização clara e organizada dos dados financeiros. Este módulo inclui um layout personalizado que destaca as informações mais relevantes para a gestão financeira da empresa, facilitando a análise e tomada de decisões estratégicas. O relatório é projetado para ser fácil de usar e interpretar, garantindo que os usuários possam acessar rapidamente as informações necessárias para monitorar o desempenho financeiro da empresa.
    """,
    'author': 'ATS Soluções',
    'depends': ['account'],
    'data': [
        'report/report_actions.xml',
        'report/report_pedido_venda_global_template.xml',
        
    ],
    'installable': True,
    'application': False,
}
