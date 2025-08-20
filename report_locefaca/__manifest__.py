# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Relatorios LoceFaca',
    'version': '1.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Relatorios personalizados',
    'description': """
    """,
    'author': 'ATS Soluções',
    'website': '',
    'depends': ['account', 'l10n_br_sale'],
    'data': [
        'report/report_saleorder_document.xml',
        'report/report_delivery_document_locefaca.xml',
        'report/report_layout_background.xml',
    ],
    'installable': True,
    'application': False,
}
