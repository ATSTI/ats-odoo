# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Payment Installment",
    "summary": "Adicionado campos para parcelamento",
    "category": "Account",
    "license": "AGPL-3",
    "author": "ATSTi Solucoes",
    "website": "http://www.atsti.com.br",
    "version": "14.0.1.0.0",
    "development_status": "Alpha",
    "depends": [
        "l10n_br_account",
        "account_payment_mode", 
    ],
    "data": [
        "views/payment_installment.xml",
        "security/ir.model.access.csv",
    ],
    "demo": [
    ],
    "installable": True,
    "auto_install": False,
}

