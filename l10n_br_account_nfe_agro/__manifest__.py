# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'NFe Informações do Agro',
    'version': '16.0.1.0',
    'category': 'Localisation',
    'license': 'AGPL-3',
    'sequence': 9,
    'summary': 'Insere na Nota Fiscal as informações de agropecuario',
    'description': """
        Este módulo permite preencher e enviar notas com informações do agropecuario:
        
        - Campos dentro da fatura para preencher ( guiaTransp / defensivo)
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': ['l10n_br_nfe','l10n_br_account',],
    'data': [
        "views/account_invoice_view.xml",
    ],
    'installable': True,
    'application': False,
}