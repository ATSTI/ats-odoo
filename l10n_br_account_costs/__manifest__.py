# Copyright (C) 2009  Renato Lima - Akretion
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Brazilian Localization Accounts costs",
    "category": "Localisation",
    "license": "AGPL-3",
    "author": "ATSTi, ",
    "website": "",
    "version": "14.0.1.0.0",
    "depends": ["l10n_br_fiscal", "l10n_br_sale", "l10n_br_account"],
    "data": [
        # Data
        # "data/company.xml",

        # Security
        # "security/ir.model.access.csv",
        # "security/l10n_br_sale_security.xml",

        # View
        "views/account_invoice_view.xml",
    ],
    "demo": [
        # Demo
        # "demo/l10n_br_account_invoice.xml",
    ],
    "installable": True,
    "auto_install": True,
    # "post_init_hook": "post_init_hook",
    # "development_status": "Production/Stable",
    "maintainers": ["carlos"],
}
