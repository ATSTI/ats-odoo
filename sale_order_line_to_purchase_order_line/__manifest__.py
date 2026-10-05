# Copyright (C) 2026 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    'name': "Converte um Pedido de venda em pedido(s) de compra",
    'version': '16.0.1.0.0',
    'category': 'Extra Tools',
    'summary': """Modulo que converte as linhas selecionadas do pedido de venda em pedido(s) de compra, 
    order lines easily.""",
    'description': """ Modulo que converte as linhas selecionadas do pedido de venda em pedido(s) de compra, separando por fornecedor (product.supplierinfo).
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'OtavioAndretta, ATSTi',
    'depends': ['sale_management', 'purchase'],
    'data': [
        'views/sale_order_views.xml',
    ],
    'images': ['static/description/banner.jpg'],
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'auto_install': False,
}
