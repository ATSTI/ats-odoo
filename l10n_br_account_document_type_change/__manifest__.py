# Copyright (C) 2026 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Account Move - Mudar tipo de documento fiscal',
    'version': '16.0.1.0',
    'category': 'Accounting',
    'license': 'AGPL-3',
    'sequence': 9,
    'summary': 'Refazer a numeração do documento fiscal ao mudar o tipo de documento',
    'description': """
        Ao mudar o tipo de documento fiscal de um documento já confirmado, 
        com o número preenchido, o sistema não recalcula com a nova serie,
        ficando com a numeração anterior, gerada no outro tipo de documento. 
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': ['account','l10n_br_fiscal',],
    'data': [
    ],
    'installable': True,
    'application': False,
}
