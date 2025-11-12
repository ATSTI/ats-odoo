# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Banco Inter - Integração com a API',
    'version': '18.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Banco Inter - Integração com a API',
    'description': """
Banco Inter - Integração com a API
Funcionalidades:
    - Geração de boletos via API do Banco Inter
    - Baixa automática de boletos via API do Banco Inter
Como usar:
    - Payment Mode precisa ser CNAB 240 para o Banco Inter
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': ['l10n_br_account_payment_order'],
    'data': [
        "security/ir.model.access.csv",
        "views/account_move.xml",
        "views/account_move_line.xml",
        "views/account_journal.xml",
        "wizard/bank_api_inter_baixa.xml",
        "data/automated_query.xml",
    ],
    'demo': [
        "demo/res_partner_bank.xml",
        "demo/ir_sequence.xml",
        "demo/account_journal.xml",
        "demo/account_payment_mode.xml",
        "demo/account_invoice.xml",
    ],
    'external_dependencies': {
        "python": [
            "erpbrasil.bank.inter",
        ]
    },
    'installable': True,
    'application': False,
}