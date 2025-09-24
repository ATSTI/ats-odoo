# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Ai Odoo',
    'version': '16.0.1.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Agente Intermediador - Contatos e Vendas',
    'description': """
        Este Módulo tem a adição do campo "Agente Intermediador" e pode estar disponivel tanto em contatos quanto em vendas
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': '',
    'depends': ['ai_oca_bridge'],
    'data': [
        # 'views/res_partner_view.xml',
        # 'views/sale_order_view.xml',
    ],
    'installable': True,
    'application': False,
}

