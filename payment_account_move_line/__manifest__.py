# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Linhas do Diário - Pagamento',
    'version': '18.0.1.0.0',
    'summary': 'Adiciona pagamento para linhas do diário',
    'description': """
Linhas do Diário - Pagamento
============================
Este módulo adiciona campos e funcionalidades relacionadas a dados de pagamento 
associados às linhas do diário, permitindo melhor controle e rastreabilidade 
no cadastro de clientes/fornecedores.
    """,
    'category': 'Localisation',
    'author': 'ATSTi Soluções',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'contributors': [
        'Carlos Silveira <carlos@atsti.com.br>',
        'Mauricio Silveira <maurs320@gmail.com>',
        'Otavio Andretta <otavio12257@gmail.com>'
    ],
    'license': 'AGPL-3',
    "depends": [
        "l10n_br_account",
        "l10n_br_account_due_list",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/account_move_line_views.xml",
        "wizard/payment_account_move_line_views.xml",
    ],
    "demo": [],
    "installable": True,
    "auto_install": False,
}
