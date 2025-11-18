# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Informações de Servidor',
    'version': '14.0.1.0.0',
    'summary': 'Adiciona informações de servidor ao parceiro',
    'description': """
Informações de Servidor
=======================
Este módulo adiciona campos e funcionalidades relacionadas a dados de servidores 
associados aos parceiros, permitindo melhor controle e rastreabilidade 
no cadastro de clientes/fornecedores.
    """,
    'category': 'Contacts/Custom',
    'author': 'ATSTi, Odoo Community Association (OCA)',
    'website': 'http://www.atsti.com.br',
    'contributors': [
        'Carlos Silveira <carlos@atsti.com.br>',
        'Mauricio Silveira <maurs320@gmail.com>',
        'Otavio Andretta <otavio12257@gmail.com>'
    ],
    'license': 'AGPL-3',
    'depends': [
        'base_setup',
        'nfe_integracao'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_server_view.xml',
        'views/res_partner_view.xml',
    ],
    'demo': [],
    'qweb': [],
    'images': [],
    'sequence': 10,
    'installable': True,
    'application': False,
    'auto_install': False,
}

