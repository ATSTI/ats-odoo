# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Relatorios de fatura ATS',
    'version': '16.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'relatorios personalizados',
    'description': """
    """,
    'author': 'ATSTi Soluções',
    'website': '',
    'depends': ['account'],
    'data': [
        'report/report_document_invoice.xml',
        'views/invoice_report.xml'

    ],
    'installable': True,
    'application': False,
}
