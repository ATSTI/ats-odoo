# -*- encoding: utf-8 -*-

{
    'name': 'Pagamento com Cheques Contas a Receber/Pagar',
    'description': """
        Adiciona a opção de adicionar juros e multa ao recebimento
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
        'br_account_payment',
    ],
    'data': [
        'wizard/payment_move_line.xml',
    ],
    'demo': [],
    'installable': True,
}
