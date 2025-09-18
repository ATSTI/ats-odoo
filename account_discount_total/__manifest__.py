# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See https://www.gnu.org/licenses/agpl

{
    'name': 'Account Discount on Total Amount',
    'version': '16.0',
    'category': 'Accounting',
    'license': 'AGPL-3',
    'summary': "Discount on Total in Invoice based on sale_discount_total (Cybrosys)",
    'description': """
        Invoice Discount for Total Amount
        =======================
        Module to manage discount on total amount in Invoice.
                as an specific amount or percentage
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/OCA/l10n-brazil',
    'depends': ['l10n_br_account', "l10n_br_account_discount"],
    'data': [
        'views/account_invoice_view.xml',
        #'views/invoice_report.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
