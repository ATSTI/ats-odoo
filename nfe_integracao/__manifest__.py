# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Responsável Financeiro & NFe Integração',
    'version': '18.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Responsável Financeiro & NFe Integração',
    'description': """
Responsável Financeiro & NFe Integração
=======================
Responsável Financeiro: Adiciona campos e funcionalidades relacionadas a dados de responsáveis financeiros
associados aos parceiros, permitindo melhor controle e rastreabilidade no cadastro de clientes/fornecedores.
NFe Integração: Usado para controlar as notas emitidas pelos clientes
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': ['base', 'pending_payments'],
    'data': [
        'views/responsavel_partner_view.xml',
    ],
    'installable': True,
    'application': False,
}