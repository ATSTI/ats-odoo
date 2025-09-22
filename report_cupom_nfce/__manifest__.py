# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Cupom NFC-e',
    'version': '16.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'relatorios personalizados',
    'description': """
    """,
    'author': 'ATSTi Soluções',
    'website': '',
    'depends': ['l10n_br_nfe', 'l10n_br_account_cpf'],
    'data': [
        'report/report_cupom_nfce.xml',
    ],
    'installable': True,
    'application': False,
}
