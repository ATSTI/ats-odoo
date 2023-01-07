# -*- coding: utf-8 -*-


{
    'name': 'Payment Installment',
    'version': '1.0',
    'category': 'Account',
    'description': """
       Permite editar parcelas geradas por Faturas de Fornecedor.
    """,
    'author': 'ATS Solucoes',
    'website': 'http://www.atsti.com.br',
    'depends': ['br_account_payment'],
    'data': [
        'views/payment_installment.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
