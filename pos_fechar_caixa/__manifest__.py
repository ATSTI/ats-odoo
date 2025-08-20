# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Pos fechamento de caixa',
    'version': '1.0',
    'category': 'Others',
    'license': 'AGPL-3',
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

