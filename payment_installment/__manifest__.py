# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See https://www.gnu.org/licenses/agpl

{
    'name': 'Adiciona aba Parcelas em Faturas',
    'version': '16.0.1.0.0',
    'category': 'Accounting',
    'license': 'AGPL-3',
    'summary': "Opção para criar parcelas em faturas",
    'description': """
        Permite criar parcelas em faturas de clientes e fornecedores
        informando o número de parcela, dia da parcela, e valor de entrada se necessário,
        e opção para editar as parcelas conforme necessidade.
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    "depends": [
        "account_payment_mode",
        "l10n_br_account",
        "l10n_br_account_payment_order",
        "l10n_br_account_due_list",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/payment_installment.xml",
    ],
    "demo": [
    ],
    "installable": True,
    "auto_install": False,
}

