# -*- encoding: utf-8 -*-

{
    'name': 'Payment Cheque',
    'description': """
        Adiciona a leitura do código de barra do cheque
    """,
    'version': '1.0',
    'category': 'Localisation',
    'author': 'ATS Solucoes',
    'website': 'http://www.atsti.com.br',
    'license': 'AGPL-3',
    'contributors': [
        'Carlos Silveira<carlos@atsti.com.br>',
    ],
    'depends': [
        'account',
    ],
    'data': [
        'views/account_payment_view.xml',
    ],
    'demo': [],
    'installable': True,
}
