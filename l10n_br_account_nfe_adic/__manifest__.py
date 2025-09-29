# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'NFe Dados Adicionais - Account Move',
    'version': '16.0.1.0',
    'category': 'localisation',
    'license': 'AGPL-3',
    'sequence': 7,
    'summary': 'Trás informações da NFe para a tela da Account Move',
    'description': """
        Este módulo trás informações da NFe para a tela da fatura, além de simplificar a tela da nfe
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': ["l10n_br_account", "l10n_br_fiscal",],
    'data': [
        "views/account_invoice_view.xml",
    ],
    'installable': True,
    'application': False,
}