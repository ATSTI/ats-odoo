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
    'name': 'Customização do Serviço de Campo',
    'version': '16.0.1.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Módulo de modificações do modulo de Serviço de Campo',
    'description': """
        Este Módulo inclui algumas customizações no Módulo FIELDSERVICE original:
        - Automatização do responsável pelas faturas
        - Marcação de horas
        - Mudanças visuais 
        - +
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': ['fieldservice', 'hr', 'base', 'account', 'l10n_br_fiscal', 'fieldservice_isp_account'],
    'data': [
        'security/ir.model.access.csv',
        'views/fsm_order_view.xml',
        'views/res_partner_view.xml',
        'views/wizard_view.xml',
        'views/account_move_view.xml',
        'report/report_paper_format.xml',
        'report/product_coupon_report.xml',
        'report/report_cliente.xml',
        'report/report_lavanderia.xml',
        'report/report_faturas_total.xml',
        'report/report_orcamento.xml',
    ],
    'installable': True,
    'application': False,
}
