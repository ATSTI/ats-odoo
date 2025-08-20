# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Cadastro de produto simplificado',
    'version': '1.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'relatorios personalizados',
    'description': """
    """,
    'author': 'ATSTi',
    'website': '',
    'depends': ['l10n_br_fiscal', 'product', 'product_sequence', 'product_multi_company'],
    'data': [
        'views/product_view.xml',
    ],
    'installable': True,
    'application': False,
}
