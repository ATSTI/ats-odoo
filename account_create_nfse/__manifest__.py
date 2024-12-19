# © 2024 Carlos R. Silveira, Maurício Rodrigues Silveira, ATSti Solucoes
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Duplicar uma fatura, copiando somente Serviço',
    'version': '14.0.0.1.0',
    'category': 'Localisation',
    'sequence': 2,
    'summary': 'ATSti Soluções',
    'description': """
        Cria nova account.move somente com Serviços, sem produtos
        No diario diversos(general), somente para poder gerar a NFe,
        pois, na fatura consta serviços tbém, que será gerado uma nota de serviço.
   """,
    'author': 'ATS Soluções',
    'website': '',
    'depends': ["l10n_br_fiscal", "l10n_br_nfse", "l10n_br_account"],
    'data': [
        'views/account_move_view.xml',
    ],
    'installable': True,
    'application': False,
}

