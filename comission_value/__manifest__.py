# -*- coding: utf-8 -*-
#############################################################################

{
    'name': 'Comission Value',
    'version': '14.0.1.1.0',
    'category': 'Sales Management',
    'summary': "Get the value comission and low the total amount in Sale Order",
    'author': 'ATSTi Soluções',
    'company': '',
    'website': '',
    'description': """

Sale Discount for Total Amount
=======================
Module to manage discount on total amount in Sale.
        as an specific amount or percentage
""",
    'depends': [
        'l10n_br_sale',
        'l10n_br_account',
                ],
    'data': [
        'views/sale_view.xml',
        # 'views/sale_order_report.xml',
        # 'views/res_config_view.xml',
        'views/account_invoice_view.xml',
    ],
    'license': 'AGPL-3',
    'application': True,
    'installable': True,
    'auto_install': False,
}
