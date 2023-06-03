# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Purchase',
    'version': '1.2',
    'category': 'Inventory/Purchase',
    'sequence': 35,
    'summary': 'Purchase orders, tenders and agreements',
    'description': "",
    'website': 'https://www.odoo.com/page/purchase',
    'depends': ['account', 'purchase'],
    'data': [
        #'security/purchase_security.xml',
        #'security/ir.model.access.csv',
    ],
    'qweb': [
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
