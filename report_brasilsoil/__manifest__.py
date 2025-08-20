# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Relatorio Brasil Soil',
    'version': '1.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'relatorios personalizados',
    'description': """
    """,
    'author': 'ATS Soluções',
    'website': '',
    'depends': ['account', 'l10n_br_sale'],
    'data': [
        'report/report_saleorder_document.xml',
    ],
    'installable': True,
    'application': False,
}
