# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'relatorio produto (30 dias)',
    'author': 'Odoo S.A',
    'category': 'Accounting/Localizations/Point of Sale',
    'license': 'LGPL-3',
    'depends': ['point_of_sale'],
    'author': 'Otavio andretta <otavio12257@gmail.com>',
    'data': [
        'security/ir.model.access.csv',
        'report/report_action.xml',
        'views/wizard.xml',
        'report/template.xml',
    ],
    'auto_install': False,
}
