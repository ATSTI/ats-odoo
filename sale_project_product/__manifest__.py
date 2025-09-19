# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.ht

{
    'name': 'Projeto - via Produto do Pedido de Venda',
    'version': '1.0',
    'category': 'Sales',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Através do produto, o Pedido de Venda pode criar Projeto / Tarefas',
    'description': """
        Este módulo permite que nas configurações do Produto, seja possível criar pelo
        Pedido de Venda um projeto ou uma Tarefa para cada Linha da Venda - Uma adaptação do módulo da OCA
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': '',
    'depends': ['sale_management', 'sale_stock', 'sale_mrp', 'sale_project', 'sale_project_copy_tasks', 'project', 'account'],
    'data': [
        'views/sale_view.xml',
        'views/stock_view.xml',
    ],
    'installable': True,
    'application': False,
}

