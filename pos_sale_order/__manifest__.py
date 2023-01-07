# -*- coding: utf-8 -*-

{
    'name': 'POS: Create Sale Order',
    'version': '1.0',
    'category': 'Point of Sale',
    'summary': 'When Invoice is selected in POS, this module will create a sale order too',
    'description': """
Create sale order via POS.
""",
    'author': 'otaviosilmunhoz@hotmail.com',
    'website': 'atsti.com.br',
    'version': '1.0.1',
    'depends': ['br_sale', 'point_of_sale'],
    'images': [],
    "data": [
        'static/src/xml/pos_sale_order.xml',
        'views/pos_session_view.xml'
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
