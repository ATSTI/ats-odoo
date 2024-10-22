# -*- coding: utf-8 -*-
#############################################################################

{
    'name': 'Sale Discount on Total Amount',
    'version': '14.0.1.1.0',
    'category': 'Sales Management',
    'summary': "Discount on Total in Sale and Invoice With Discount Limit and Approval (by Cybrosys) - adapted l10n-brazil",
    'author': 'ATSTi Soluções',
    'company': '',
    'website': '',
    'description': """

Sale Discount for Total Amount
=======================
Module to manage discount on total amount in Sale.
        as an specific amount or percentage
""",
    'depends': ['l10n_br_sale',
                'account_discount_total', 'l10n_br_delivery'
                ],
    'data': [
        'views/sale_view.xml',
        # 'views/account_invoice_view.xml',
        #'views/invoice_report.xml',
        'views/sale_order_report.xml',
        'views/res_config_view.xml',

    ],
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'application': True,
    'installable': True,
    'auto_install': False,
}
