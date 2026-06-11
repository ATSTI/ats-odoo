# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Consultar Pagamentos Pendentes (USERS)',
    'version': '1.0',
    'summary': 'Consulta pagamentos de determinada empresa',
    'description': """
Consulta de Pagamentos Pendentes
================================
Este módulo adiciona campos e funcionalidades relacionadas a dados de pagamentos 
pendentes associados às empresas, permitindo melhor controle e rastreabilidade 
no cadastro de clientes/fornecedores.
    """,
    'category': 'Contacts/Custom',
    'author': 'ATSTi Soluções',
    'maintainer': 'Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'contributors': [
        'Carlos Silveira <carlos@atsti.com.br>',
        'Mauricio Silveira <maurs320@gmail.com>',
        'Otavio Andretta <otavio12257@gmail.com>'
    ],
    'license': 'AGPL-3',
    'depends': ['base_setup', 'web', 'l10n_br_account'],
    'data': [
        "views/assests.xml"
    ],
    'sequence': 10,
    'installable': True,
    'application': False,
    'auto_install': False,
}

