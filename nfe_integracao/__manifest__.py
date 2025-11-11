# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': "Responsável Financeiro & NFe Integração",
    'version': '18.0.1.0.0',
    'summary': 'Responsável Financeiro & NFe Integração',
    'description': """
Responsável Financeiro & NFe Integração
=======================
Responsável Financeiro: Adiciona campos e funcionalidades relacionadas a dados de responsáveis financeiros
associados aos parceiros, permitindo melhor controle e rastreabilidade no cadastro de clientes/fornecedores.
NFe Integração: Usado para controlar as notas emitidas pelos clientes
    """,
    'category': 'Contacts/Custom',
    'author': 'ATSTi Soluções',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'contributors': [
        'Carlos Silveira <carlos@atsti.com.br>',
        'Mauricio Silveira <maurs320@gmail.com>',
        'Otavio Andretta <otavio12257@gmail.com>'
    ],
    'license': 'AGPL-3',
    'depends': [
        'base',
    ],
    'data': [
        'views/responsavel_partner_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
