# -*- coding: utf-8 -*-
# © 2004-2010 OpenERP SA
# © 2019 Carlos Silveira <crsilveira@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Mercado Livre Odoo',
    'version': '14.0.1.0.0',
    'category': 'Product',
    'author': 'Carlos R. Silveira '
              ,
    'license': 'AGPL-3',
    'depends': ['base', 'account', 'l10n_br_fiscal', 'sale', 'sale_stock_operating_unit', 'mail'],
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'views/meli_view.xml',
        'views/product_view.xml',
        'views/sale_order_line_view.xml',
        ],
    'installable': True,
    'images': [],
}
