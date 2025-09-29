# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Preço de Venda como Base no Preço de Compra',
    'version': '16.0',
    'category': 'Product',
    'license': 'AGPL-3',
    'summary': 'Opção para definir preço de Venda.',
    'description': """
        Esse Módulo permite definir o preço de venda 
        usando por base os itens do
        pedido de compra.
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': [
        'purchase','product_sale_margin'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_itens_view.xml',
        'views/purchase_views.xml',
    ],
    'installable': True,
    'application': False,
}
