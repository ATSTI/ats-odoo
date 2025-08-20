# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Conats Analiticas Criar',
    'version': '1.0',
    'category': 'Others',
    'license': 'AGPL-3',
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

