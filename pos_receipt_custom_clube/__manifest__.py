# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Recibo POS customização',
    'author': 'Odoo S.A',
    'category': 'Accounting/Localizations/Point of Sale',
    'description': """Customização para o recibo da Clube sao pedro, pos""",
    'license': 'LGPL-3',
    'depends': ['point_of_sale'],
    'data': [
        #'views/assets.xml',
    ],
    'qweb': [
        'static/src/xml/OrderReceipt.xml',
    ],
    'auto_install': False,
}
