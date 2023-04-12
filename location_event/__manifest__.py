# -*- coding: utf-8 -*-
{
    'name': "Product location event",

    'summary': """
        costumizacao Myplace locação""",

    'description': """
        Long description of module's purpose
    """,

    'author': "ATSTI",
    'website': "http://www.atsti.com.br",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['event','product'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/event_view.xml',
        'views/product_view.xml',
        ],
    # only loaded in demonstration mode
    'demo': [
    ],
}