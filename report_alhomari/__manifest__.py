# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


{
    'name': 'Relatorio Alhos Mari',
    'version': '16.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'relatorios personalizados',
    'description': """
    """,
    'author': 'ATSTi Soluções',
    'website': '',
    'depends': ['account', 'l10n_br_sale','account_payment_mode'],
    'data': [
        'report/report_saleorder_document.xml',
        'report/account_move_alhomari_report_templates.xml',
    ],
    'installable': True,
    'application': False,
}
