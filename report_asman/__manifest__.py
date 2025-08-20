# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Relatorios Asman',
    'version': '1.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'relatorios personalizados',
    'description': """
    """,
    'author': 'ATS Soluções',
    'website': '',
    'depends': ['l10n_br_sale', 'report_cabecalho', 'l10n_br_purchase'],
    'data': [
        'report/report_delivery_document_asman.xml',
        'report/report_purchase_asman.xml',
        'views/report_orcamento.xml'
    ],
    'installable': True,
    'application': False,
}
