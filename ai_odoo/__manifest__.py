# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Ai Odoo',
    'version': '16.0.1.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Integração com OpenAI - dados, faturas, produtos e muito mais',
    'description': """
        Este módulo tem como função integrar um agente de IA no chat do odoo, com ele você conseguirá informações de forma
        mais rápida e eficiente, usando a linguagem humana para poder criar faturas, saber vendas, faturas em aberto, top sellers, clientes que mais compram, entre outras coisas
        """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Otávio Andretta,Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': '',
    'depends': ['ai_oca_bridge'],
    'data': [
        # 'views/res_partner_view.xml',
        # 'views/sale_order_view.xml',
    ],
    'installable': True,
    'application': False,
}

