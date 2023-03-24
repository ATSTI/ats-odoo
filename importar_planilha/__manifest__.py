# © 2022 Carlos R. Silveira, Manoel dos Santos, ATSti Solucoes
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Importar Planilha',
    'version': '1.0',
    'category': 'Others',
    'sequence': 2,
    'summary': 'ATSti Sistemas',
    'description': """
        Importa Planilha de Produtos e Cliente
   """,
    'author': 'ATS Soluções',
    'website': '',
    'depends': ["partner_manual_rank"],
    'data': [
        'security/ir.model.access.csv',
        'wizard/importar_view.xml',
    ],
    'installable': True,
    'application': False,
}

