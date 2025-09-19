# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.ht

{
    'name': 'Shopee Odoo',
    'version': '1.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Módulo de Integração do Odoo com a Shopee',
    'description': """
        Este módulo tem como finalidade a integração de diversos setores da Shopee com o Odoo, entre estas está:
        - Sincronização de pedidos
        - Ajuste de preços via Odoo
        - Ajuste de estoque via Odoo
        - Envio de notas fiscais
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': '',
    'depends': ['base', 'account', 'l10n_br_fiscal', 'sale'],
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'views/shopee_view.xml',
        'views/product_view.xml',
        ],
    'installable': True,
    'application': False,
}