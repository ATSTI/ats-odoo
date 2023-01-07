# -*- encoding: utf-8 -*-

{
    'name': 'Pagamento Juros/Multa com Impressao',
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
        'account_interests'
    ],
    'data': [
        #'views/account_payment_view.xml',
        'wizard/payment_move_line.xml',
        'report/report_invoice_cupom.xml',
        'report/report_invoice_cupom_templates.xml',
    ],
    'demo': [],
    'installable': True,
}
