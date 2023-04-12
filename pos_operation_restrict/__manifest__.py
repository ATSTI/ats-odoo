# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
# Please see LICENSE file.
#################################################################################

{
    'name': 'POS: User to set discount and price',
    'version': '1.0',
    'category': 'Point of Sale',
    'summary': 'This module allow the restriction in pos',
    'description': """
This module allow the restriction in pos.
""",
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'website': 'http://www.acespritech.com',
    'price': 15.00,
    'currency': 'EUR',
    'version': '1.0.1',
    'depends': ['base', 'point_of_sale'],
    'images': ['static/description/main_screenshot.png'],
    "data": [
        'views/pos_operation_restrict_view.xml',
        'views/res_users_view.xml',
        'views/point_of_sale_view.xml',
    ],
    'qweb': [
            'static/src/xml/pos.xml'
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
