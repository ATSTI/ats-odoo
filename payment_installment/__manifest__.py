# -*- coding: utf-8 -*-


{
    'name': 'Payment Installment',
    'version': '14.0.1.0.0',
    'category': 'Account',
    'description': """
       Permite criar e editar parcelas geradas para Faturas.
    """,
    'author': 'ATSTi Solucoes',
    'website': 'http://www.atsti.com.br',
    'depends': [
        'l10n_br_account',
        'account_payment_mode',        
                ],
    'data': [
        'views/payment_installment.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}

