# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Contas Analiticas Criar',
    'version': '16.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'ATSti Sistemas',
    'description': """
        Importa Planilha de Produtos e Cliente
   """,
    'author': 'ATSTi,Odoo Community Association (OCA)',
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

