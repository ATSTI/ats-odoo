# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Importar Planilha',
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
    'depends': ["partner_manual_rank"],
    'data': [
        'security/ir.model.access.csv',
        'wizard/importar_view.xml',
    ],
    'installable': True,
    'application': False,
}

