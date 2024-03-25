# © 2024 Carlos R. Silveira, Maurício Rodrigues Silveira, ATSti Solucoes
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Pos fechamento de caixa',
    'version': '1.0',
    'category': 'Others',
    'sequence': 2,
    'summary': 'ATSti Sistemas',
    'description': """
        Tela do fechamento de caixa do ponto de venda
   """,
    'author': 'ATS Soluções',
    'website': '',
    'depends': ["point_of_sale", "account"],
    'data': [
        'security/ir.model.access.csv',
        'views/fechar_caixa.xml',
    ],
    'installable': True,
    'application': False,
}

