# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Relatorios Vendas & Compras',
    'version': '16.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'relatorios comparativos entre vendas e compras',
    'description': """
    """,
    'author': 'ATSTi Soluções',
    'website': '',
    'depends': ['sale'],
    'data': [
        'security/ir.model.access.csv',
        'report/report_sale_balance.xml',
        'report/sale_balance.xml',
        'wizard/report_sale_balance_view.xml',
    ],
    'installable': True,
    'application': False,
}
