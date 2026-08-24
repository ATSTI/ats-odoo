# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Informações Fiscais do Parceiro',
    'version': '16.0.1.0',
    'category': 'localisation',
    'license': 'AGPL-3',
    'sequence': 7,
    'summary': 'Traz informações do Parceiro para a Fatura automatico',
    'description': """
        Este módulo trás informações Fiscais do Parceiro para a Fatura automaticamente, como o Comentário Fiscal do Parceiro.
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': ["l10n_br_account", "l10n_br_fiscal"],
    'data': [
        "views/res_partner.xml",
    ],
    'installable': True,
    'application': False,
}