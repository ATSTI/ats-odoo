# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Relatio POS Tipo de Venda',
    'version': '1.0.1',
    'category': 'Point Of Sale',
    'sequence': 20,
    'summary': 'Relatorio por Tipo de Venda',
    'description': """
    """,
    'depends': ['product_sale_margin'],
    'data': [
        'views/pos_order_report_view.xml',
    ],
    'installable': True,
    'application': False,
}
