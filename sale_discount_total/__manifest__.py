# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See https://www.gnu.org/licenses/agpl

{
    'name': 'Sale Discount on Total Amount',
    'version': '16.0',
    'category': 'Sales Management',
    'license': 'AGPL-3',
    'summary': 'Discount on Total in Sale and Invoice With Discount Limit and Approval (by Cybrosys) - adapted l10n-brazil',
    'description': """
        Sale Discount for Total Amount
=======================
Module to manage discount on total amount in Sale.
        as an specific amount or percentage
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': '',
    'depends': [
        'l10n_br_sale',
        'sale_discount_display_amount',
        'account_discount_total',
        'l10n_br_delivery',
                ],
    'data': [
        'views/sale_view.xml',
        # 'views/sale_order_report.xml',
        'views/res_config_view.xml',
    ],
    'installable': True,
    'application': False,
}

