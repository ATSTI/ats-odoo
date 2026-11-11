# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See https://www.gnu.org/licenses/agpl

{
    'name': 'Invoice Report Analytic Customization',
    'version': '16.1.0',
    'category': 'Accounting',
    'license': 'AGPL-3',
    'summary': "Datas e prazos de estágios para Contas Analíticas",
    'description': """""",
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': ['account'],
    'data': [
        'report/account_analytic_report_view.xml',
    ],
    'installable': True,
}