# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{  
    'name': 'Payment Account Move Line',
    'version': '16.0.1.0',
    'category': 'Localisation',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Finaceiro : Contas a Receber e Pagar',
    'description': """
        Este módulo tem as funções de pagamento e recebimento de linhas das faturas
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': ['l10n_br_account', 'l10n_br_account_due_list',],
    'data': [
        'security/ir.model.access.csv',
        'views/account_move_line_views.xml',
        'wizard/payment_account_move_line_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
