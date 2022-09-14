# © 2021 Carlos R. Silveira, Manoel dos Santos, ATSti Solucoes
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Invoice - Renegotiate',
    'version': '1.0',
    'category': 'Others',
    'sequence': 2,
    'summary': 'ATSti Sistemas',
    'description': """
        Baixa as Faturas selecionadas
        e cria uma nova fatura informando em cada
        linha as faturas selecionadas.
        IMPORTANTE:
          Precisa criar um diário para Acordo: 
             - acordo
          e contas de lançamento da Fatura:
             - c-acordo : Conta de débito (Tipo: A Receber)
             - p-acordo : Conta de crédito
   """,
    'author': 'ATS Soluções',
    'website': '',
    'depends': ['account','br_account_payment'],
    'data': [
        'wizard/execute_renegotiate.xml'
    ],
    'installable': True,
    'application': False,
}

