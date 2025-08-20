# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


{
    'name': 'Criação de projeto do pedido de venda (produto)',
    'version': '1.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'cria um projeto a partir de um pedido de venda que seja produto',
    'description': """
    """,
    'author': 'ATS Soluções',
    'website': '',
    'depends': ['sale', 'sale_stock', 'sale_mrp', 'sale_project', 'sale_project_service_tracking_copy_tasks', 'project', 'account'],
    'data': [
        'views/sale_view.xml',
        'views/stock_view.xml',
    ],
    'installable': True,
    'application': False,
}
