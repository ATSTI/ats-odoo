# -*- coding: utf-8 -*-
#############################################################################

{
    'name': 'Account Discount on Total Amount',
    'version': '14.0.1.1.0',
    'category': 'Accounting',
    'summary': "Discount on Total in Invoice based on sale_discount_total (Cybrosys)",
    'author': 'ATSTi Soluções',
    'company': 'ATSTi Soluções',
    'website': '',
    'description': """

Invoice Discount for Total Amount
=======================
Module to manage discount on total amount in Invoice.
        as an specific amount or percentage
""",
    'depends': ['l10n_br_account'],
    'data': [
        'views/account_invoice_view.xml',
        #'views/invoice_report.xml',
    ],
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'application': True,
    'installable': True,
    'auto_install': False,
}
