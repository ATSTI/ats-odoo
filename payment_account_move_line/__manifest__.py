# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Linhas do Diário - Pagamento',
    'version': '18.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Adiciona pagamento para linhas do diário',
    'description': """
    Linhas do Diário - Pagamento
============================
Este módulo adiciona campos e funcionalidades relacionadas a dados de pagamento 
associados às linhas do diário, permitindo melhor controle e rastreabilidade 
no cadastro de clientes/fornecedores.
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': [
        'l10n_br_account',
        'l10n_br_account_due_list',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_move_line_views.xml',
        'wizard/payment_account_move_line_views.xml',
    ],
    'installable': True,
    'application': False,
}