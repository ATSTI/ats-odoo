# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.ht

{
    'name': 'Meli - Odoo',
    'version': '16.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Módulo de Integração do Odoo com o Mercado Livre',
    'description': """
        Este módulo tem como finalidade a integração de diversos setores do Mercado Livre com o Odoo, entre estas está:
        - Sincronização de pedidos
        - Ajuste de preços via Odoo
        - Ajuste de estoque via Odoo
        - Envio de notas fiscais
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': '',
    'depends': ['base', 'account', 'l10n_br_fiscal', 'sale', 'sale_stock_operating_unit'],
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'views/meli_view.xml',
        'views/product_view.xml',
        'views/sale_order_line_view.xml',
        ],
    'installable': True,
    'application': False,
}