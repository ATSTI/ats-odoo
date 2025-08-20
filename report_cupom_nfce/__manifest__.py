# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Cupom NFC-e',
    'version': '1.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'relatorios personalizados',
    'description': """
    """,
    'author': 'ATS Soluções',
    'website': '',
    'depends': ['l10n_br_nfe', 'l10n_br_account_cpf'],
    'data': [
        'report/report_cupom_nfce.xml',
        # 'report/report_paper_format_lk.xml',

    ],
    'installable': True,
    'application': False,
}
