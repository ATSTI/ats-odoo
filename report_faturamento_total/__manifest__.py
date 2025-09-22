# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Relatorio de Faturamento Total',
    'version': '16.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Modulo de Relatorio de Faturamento Total',
    'description': """
    """,
    'author': 'ATSTi Soluções',
    'website': '',
    'depends': ['base', 'account', 'l10n_br_fiscal'],
    'data': [
        'report/report_paper_format.xml',
        'report/report_faturas_total.xml',
    ],
    'installable': True,
    'application': False,
}
