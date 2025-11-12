# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Informações de Servidor',
    'version': '18.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Informações de servidor ao parceiro',
    'description': """
Informações de Servidor
=======================
Este módulo adiciona campos e funcionalidades relacionadas a dados de servidores 
associados aos parceiros, permitindo melhor controle e rastreabilidade 
no cadastro de clientes/fornecedores.
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'OtavioAndretta, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': [
        'base',
        'nfe_integracao'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_server_view.xml',
        'views/res_partner_view.xml',
    ],
    'installable': True,
    'application': False,
}
