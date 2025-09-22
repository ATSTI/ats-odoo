# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Nota de Serviço',
    'version': '16.0.1.0',
    'category': 'Accounting',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Impressão de Nota de Servico',
    'description': """
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': '',
    'depends': ['account'],
    'data': [
        'report/account_move_service_report_templates.xml',
        'report/account_move_service_report.xml',
    ],
    'installable': True,
    'application': False,
}