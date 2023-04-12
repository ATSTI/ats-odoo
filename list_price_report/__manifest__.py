# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Sales Price List Report',
    'version': '1.0',
    'category': 'Sales',
    'sequence': 15,
    'summary': 'Price List Report',
    'description': """
    """,
    'website': 'https://www.odoo.com/page/crm',
    'depends': ['sales_team'],
    'data': [
        'report/list_price_report_views.xml',
    ],
    'demo': [
    ],
    'css': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
