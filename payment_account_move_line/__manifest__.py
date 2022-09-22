# Copyright (C) 2022 - Carlos R. Silveira - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Payment Account Move Line",
    "category": "Localisation",
    "license": "AGPL-3",
    "author": "ATSTi Solucoes",
    "website": "https://github.com/ATSTI/ats-odoo",
    "summary": "Finaceiro : Contas a Receber e Pagar",
    "depends": [
        "l10n_br_account",
        "l10n_br_account_due_list",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/account_move_line_views.xml",
        "wizard/payment_account_move_line_views.xml",
    ],
    "demo": [],
    "installable": True,
    "auto_install": False,
}
