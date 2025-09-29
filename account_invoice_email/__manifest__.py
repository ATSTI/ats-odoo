# Copyright (C) 2025 - ATSTi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Account Move Email Sender',
    'version': '16.0.1.0.0',
    'category': 'Accounting',
    'license': 'AGPL-3',
    'sequence': 10,
    'summary': 'Envio automático de emails de cobrança para faturas',
    'description': """
Account Move Email Sender
==========================

Este módulo permite o envio automático de emails para faturas
com vencimento específico ou recém-criadas.

Funcionalidades:
- Envio de emails de cobrança ou aviso de vencimento.
- Controle de envio para evitar duplicidade.
- Inclusão automática de anexos relacionados às faturas.
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': ['account','mail',],
    'data': [
        'data/mail_template.xml',
        'data/account_email_cron.xml',
        'views/account_move.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}