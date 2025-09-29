# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Cadastro de Cliente simplificado',
    'version': '1.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Simplifica o cadastro de clientes versão Fiscal',
    'description': """
        Alterações na tela de cadastro de clientes para simplificar o uso.
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': ['l10n_br_base', 'l10n_br_fiscal', 'l10n_br_account', 'account_payment_partner' ],
    'data': [
        'views/partner_view.xml',
    ],
    'installable': True,
    'application': False,
}
