# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Brasil – Integração API Banco Inter',
    'version': '14.0.1.0.0',
    'category': 'Accounting',
    'license': 'AGPL-3',
    'sequence': 10,
    'summary': 'Integra integração com APIs bancárias (inter) para pagamentos e conciliações no Brasil',
    'description': """
        Este módulo adiciona funcionalidade de integração com APIs do banco “Inter” para:
        - Consulta de transações bancárias via API;
        - Importação automática de extratos;
        - Conciliação automática entre lançamentos financeiros e movimentos bancários;
        - Outras rotinas de automação bancária específicas para o banco Inter.
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio Silveira, ATSTi',
    'website': '',
    'depends': [
        'l10n_br_account_payment_order',
    ],
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
    'auto_install': False,

}