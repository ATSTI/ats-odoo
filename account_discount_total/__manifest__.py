# -*- coding: utf-8 -*-
#############################################################################

{
    'name': 'Account - discount on total amount',
    'version': '14.0.1.1.0',
    'category': 'Accounting',
    'summary': "Desconto no total da fatura por valor ou percentual",
    'author': 'ATSTi Soluções',
    'company': 'ATSTi Soluções',
    'website': '',
    'description': """
""",
    'depends': ['l10n_br_account', "l10n_br_account_discount"],
    'data': [
        'views/account_invoice_view.xml',
        #'views/invoice_report.xml',
    ],
    'images': [],
    'license': 'AGPL-3',
    'application': True,
    'installable': True,
    'auto_install': False,
}
