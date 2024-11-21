# -*- coding: utf-8 -*-
#############################################################################

{
    'name': 'Purchase Discount on Total Amount',
    'version': '14.0.1.1.0',
    'category': 'Sales Management',
    'summary': "Discount on Total in Purchase and Invoice With Discount Limit and Approval (by Cybrosys) - adapted l10n-brazil",
    'author': 'ATSTi Soluções',
    'company': '',
    'website': '',
    'description': """

Purchase Discount for Total Amount
=======================
Module to manage discount on total amount in Purchase.
        as an specific amount or percentage
""",
    'depends': [
        'l10n_br_purchase',
        'account_discount_total',
        'l10n_br_delivery',
                ],
    'data': [
        'views/purchase_view.xml',
        'views/purchase_order_report.xml',
        # 'views/res_config_view.xml',
    ],
    'license': 'AGPL-3',
    'application': True,
    'installable': True,
    'auto_install': False,
}
