# © 2022 Carlos R. Silveira, Manoel dos Santos, ATSti Solucoes
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Conats Analiticas Criar',
    'version': '1.0',
    'category': 'Others',
    'sequence': 2,
    'summary': 'ATSti Sistemas',
    'description': """
        Importa Planilha de Produtos e Cliente
   """,
    'author': 'ATS Soluções',
    'website': '',
    'depends': [
        'analytic',
        'base_setup',
        "account",
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/analytic_copy.xml',
    ],
    'installable': True,
    'application': False,
}

