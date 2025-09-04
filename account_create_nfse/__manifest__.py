# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Duplicar uma fatura, copiando somente Serviço',
    'version': '16.0',
    'category': 'Localisation',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'ATSti Soluções',
    'description': """
        Cria nova account.move somente com Serviços, sem produtos
        No diario diversos(general), somente para poder gerar a NFe,
        pois, na fatura consta serviços tbém, que será gerado uma nota de serviço.
   """,
    'author': 'ATSTi,Odoo Community Association (OCA)',
    'website': '',
    'depends': ["l10n_br_fiscal", "l10n_br_nfse", "l10n_br_account"],
    'data': [
        'views/account_move_view.xml',
    ],
    'installable': True,
    'application': False,
}

