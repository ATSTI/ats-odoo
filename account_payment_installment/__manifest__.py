# -*- coding: utf-8 -*-


{
    'name': 'Account Payment Installment',
    'version': '1.0',
    'category': 'Account',
    'description': """
       Permite editar parcelas geradas por Faturas de Fornecedor.
    """,
    'author': 'ATS Solucoes',
    'website': 'http://www.atsti.com.br',
    'depends': ['br_account', 'br_purchase'],
    'data': [
        'views/account_invoice.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
