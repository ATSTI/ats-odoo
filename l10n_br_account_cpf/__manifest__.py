# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "NFCe com cpf,",
    "category": "Localisation",
    "license": "AGPL-3",
    "author": "ATSTi, ",
    "website": "",
    'description': """
        Grava o cpf no cadastro do cliente quando é do tipo consumidor anonimo
   """,
    "version": "14.0.1.0.0",
    "depends": ["l10n_br_fiscal", "l10n_br_account"],
    "data": [
        # View
        "views/account_invoice_view.xml",
    ],
    "demo": [
    ],
    "installable": True,
    "auto_install": False,
    "maintainers": ["carlos"],
}
