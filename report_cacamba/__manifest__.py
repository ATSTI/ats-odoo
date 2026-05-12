# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Relatorio de locação de cacambas',
    'version': '16.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Relatorios de locação de cacambas',
    'description': """
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Otávio Andretta <otavio12257@gmail.com>',
    'website': '',
    'depends': ['account', 'base'],
    'data': [
        'report/report_action.xml',
        'report/report_locacao_dica.xml',
        'report/report_locacao_lilio.xml',

    ],
    'installable': True,
    'application': False,
}
