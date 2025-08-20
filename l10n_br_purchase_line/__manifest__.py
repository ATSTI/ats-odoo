# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html#

{
    'name': 'Linha para produto in Purchase',
    'version': '1.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'cadastro de produto na compra com linha unica',
    'description': """
    """,
    'author': 'ATS Soluções',
    'website': '',
    'depends': ['l10n_br_purchase'],
    'data': [
        'views/line_product_view.xml'

    ],
    'installable': True,
    'application': False,
}
