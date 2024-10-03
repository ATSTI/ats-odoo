# © 2022 Carlos R. Silveira, Manoel dos Santos, ATSti Solucoes
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Copiar Fatura',
    'version': '1.0',
    'category': 'Others',
    'sequence': 2,
    'summary': 'ATSti Sistemas',
    'description': """
        Copiar a fatura e a linha de produtos
   """,
    'author': 'ATS Soluções',
    'website': '',
    'depends': ["l10n_br_fiscal", "l10n_br_account"],
    'data': [
        'security/ir.model.access.csv',
        'views/copiar_view.xml',
    ],
    'installable': True,
    'application': False,
}

