# Copyright (C) 2025 - ATSTi
# License AGPL-3 - Veja https://www.gnu.org/licenses/agpl

{
    'name': 'Custom Product Template Locations',
    'version': '16.0.1.0.0',
    'category': 'Inventory',
    'license': 'AGPL-3',
    'summary': 'Modifica o formulário do produto para exibir campos de estoque sem restrição de grupo',
    'description': """
        Este módulo altera a view do formulário de Product Template herdada de stock,
        removendo restrições de grupo (como group="no_one") e mostrando os campos:
        - Counterpart Locations: property_stock_production e property_stock_inventory
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': ['stock', 'product'],
    'data': [
        'views/product_template_view.xml',
    ],
    'installable': True,
    'application': False,
}