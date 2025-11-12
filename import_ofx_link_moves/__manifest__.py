# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Import OFX - Link Moves',
    'version': '18.0',
    'category': 'Banking addons',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Relacionando Fatureas na importação do OFX',
    'description': """
Esse módulo permitea ligação da fatura de certo cliente as linhas de extrato da importação do OFX
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': ['account_statement_import_ofx'],
    'data': [],
    'installable': True,
    'application': False,
}