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
    'name': 'Relatorio Financeiro',
    'version': '1.0',
    'category': 'Others',
    'sequence': 2,
    'summary': 'Contas a Pagar/Receber Relatorio',
    'description': """
    """,
    'author': 'ATS Soluções',
    'website': '',
    'depends': ['account'],
    'data': [
        'views/account_move_report.xml',
        'views/account_move_report_rec.xml',
        'security/ir.model.access.csv',
        'report/contaspagar_report_templates.xml',
        'report/contaspagar_report.xml',
        'report/contasreceber_report_templates.xml',
        'report/contasreceber_report.xml',

    ],
    'installable': True,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
