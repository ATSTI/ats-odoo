# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Relatorios LoceFaca',
    'version': '16.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Relatorios personalizados',
    'description': """
    """,
    'author': 'ATSTi Soluções',
    'website': '',
    'depends': ['account', 'l10n_br_sale','stock','report_cabecalho'],
    'data': [
        'report/report_delivery_document_locefaca.xml',
    ],
    'installable': True,
    'application': False,
}
