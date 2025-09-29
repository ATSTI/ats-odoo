# Copyright (C) 2025 - ATSTi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'NFe Error Message',
    'version': '16.0.1.0',
    'category': 'Localisation',
    'license': 'AGPL-3',
    'sequence': 5,
    'summary': 'Quando com erro, Mostra a mensagem antes de enviar a nota',
    'description': """
        Este módulo mostra ao usuario possiveis erros que a nota pode ter,
        mesmo antes de enviá-la.
        -Mostrando mensagens especificando o erro.
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': ["l10n_br_account", "l10n_br_nfe"],
    'data': [
        "views/account_invoice_view.xml",
    ],
    'installable': True,
    'application': False,
}
