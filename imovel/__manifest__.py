# -*- coding: utf-8 -*-
# © 2004-2010 OpenERP SA
# © 2019 Carlos Silveira <crsilveira@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Imovel',
    'version': '14.0.1.0.0',
    'category': 'Product',
    'author': 'Carlos R. Silveira '
              ,
    'license': 'AGPL-3',
    'depends': ['account', 'product', 'br_base', 'br_zip', 'contract'],
    'data': [
        'views/imovel_view.xml',
        'views/contract_view.xml',
        'views/account_invoice_view.xml',
        'views/report_invoice_document.xml',
        ],
    'installable': True,
    'images': [
        'static/description/icon.png',
    ],
}
