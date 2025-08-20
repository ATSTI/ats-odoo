# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Nota de Serviço',
    'version': '1.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Impressão de Nota de Servico',
    'description': """
    """,
    'author': 'ATS Soluções',
    'website': '',
    'depends': ['account'],
    'data': [
        'report/account_move_service_report_templates.xml',
        'report/account_move_service_report.xml',

    ],
    'installable': True,
    'application': False,
}
