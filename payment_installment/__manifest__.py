# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Payment Installment",
    "summary": "Adicionado campos para parcelamento",
    "category": "Account",
    "license": "AGPL-3",
    "author": "ATSTi",
    "website": "http://www.atsti.com.br",
    "version": "16.0",
    "development_status": "Alpha",
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

