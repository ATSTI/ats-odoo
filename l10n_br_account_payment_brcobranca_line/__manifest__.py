# Copyright (C) 2026 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Brcobranca - gerando boleto de uma linha de pagamento',
    'version': '16.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Brcobranca - gerando boleto de uma linha de pagamento',
    'description': """
        Permite gerar boleto de apenas uma linha ou mais do Contas a Receber,
        sem a necessidade de gerar o boleto de toda a fatura.
        Para isso, basta acessar a linha do contas a receber e clicar no botão 'PDF Boleto';

        IMPORTANTE 1: na fatura o modo de pagamento não deve ser do tipo CNAB(Boleto)

        IMPORTANTE 2: não é obrigatório mas tem mais sentido usar este módulo
        junto ao modulo payment_installment, pois, este permite alterar 
        a forma de pagamento em cada parcela(linha do contas a receber).
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos Silveira, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': ['l10n_br_account_payment_brcobranca'],
    'data': [
        "views/account_move_line.xml",
    ],
    'demo': [
    ],
    'installable': True,
    'application': False,
}