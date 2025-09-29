# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Cadastro de Cliente Fiscal Operation',
    'version': '1.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'summary': 'Adiciona campo Fiscal Operation no cadastro de clientes',
    'description': """
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': ['l10n_br_base','l10n_br_fiscal'],
    'data': [
        'views/partner_view.xml',
    ],
    'installable': True,
    'application': False,
}
