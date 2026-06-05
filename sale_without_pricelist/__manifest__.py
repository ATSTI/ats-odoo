# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.ht

{
    'name': 'Sale Without Pricelist',
    'version': '1.0',
    'category': 'Inventory/Stock',
    'license': 'AGPL-3',
    'sequence': 5,
    'summary': 'Permite ignorar o calculo do preço unitário com base na tabela de preços.',
    'description': """
        Este módulo estende o comportamento do cáculo do preço unitário em linhas do pedido de venda,
        ignorando a tabela de preços e utilizando o preço definido no produto ou o preço unitário já definido na linha do pedido.
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': ['stock', 'repair'],
    'data': [],
    'installable': True,
    'application': False,
}