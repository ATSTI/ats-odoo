# © 2024 Carlos R. Silveira, Maurício Rodrigues Silveira, ATSti Solucoes
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Duplicar uma fatura, copiando somente produtos',
    'version': '14.0.0.1.0',
    'category': 'Localisation',
    'sequence': 2,
    'summary': 'ATSti Sistemas',
    'description': """
        Cria nova account.move somente com produtos, sem serviços
   """,
    'author': 'ATS Soluções',
    'website': '',
    'depends': ["l10n_br_fiscal", "l10n_br_account"],
    'data': [
        'views/account_move_view.xml',
        # 'wizard/account_move_other_nfe_view.xml',
    ],
    'installable': True,
    'application': False,
}

