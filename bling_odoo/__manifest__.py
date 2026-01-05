# -*- coding: utf-8 -*-
# © 2004-2010 OpenERP SA
# © 2019 Carlos Silveira <crsilveira@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Bling Odoo',
    'version': '12.0.1.0.0',
    'category': 'Sale',
    'author': 'Mauricio R. Silveira',
    'license': 'AGPL-3',
    'depends': ['base', 'account','sale', 'mail',],
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'views/bling_view.xml',
        ],
    'installable': True,
    'images': [],
}
