# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Consulta Pendências',
    'version': '1.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Consulta de pendências',
    'description': """
Consulta de Pendências
=======================
Este módulo adiciona campos e funcionalidades relacionadas a dados de pendências 
associadas aos parceiros, permitindo melhor controle e rastreabilidade 
no cadastro de clientes/fornecedores.
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': ['base', 'account', 'website'],
    'data': [
        'views/res_company.xml',
    ],
    'installable': True,
    'application': False,
}
