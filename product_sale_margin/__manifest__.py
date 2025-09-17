# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Margem de Vendas no Produto',
    'version': '16.0',
    'category': 'Sale',
    'license': 'AGPL-3',
    'summary': 'Definir Margem de Venda no Produto',
    'description': """
            Esse Módulo permite definir a margem de venda diretamente no produto.
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos Silveira, Mauricio-ATS, ATSTi',
    'website': '',
    'depends': [
        'product', 'mrp'
    ],
    'data': [
        'views/product_views.xml',
    ],
    'installable': True,
    'application': False,
}