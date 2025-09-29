# Copyright (C) 2025 - ATSTi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Payment Account Move Line',
    'version': '16.0.1.0.0',
    'category': 'Accounting',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Financeiro: Pagamento e Recebimento de Linhas de Faturas',
    'description': """
Payment Account Move Line
==========================

Este módulo adiciona funcionalidades para pagamento e recebimento
de linhas específicas das faturas.

Funcionalidades:
- Permite pagar ou receber linhas individuais de faturas;
- Facilita o controle financeiro detalhado.
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
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
    'auto_install': False,
}