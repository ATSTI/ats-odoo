# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Brazilian Localization Accounts Mensage",
    "summary": """
        Adiciona mensagem de validação campos obrigatorios do cliente
        na fatura, e deixa algumas msg de validação da nfe mais fáceis.
    """,
    "category": "Localisation",
    "license": "AGPL-3",
    "author": "ATSTi, ",
    "website": "",
    "version": "14.0.1.0.0",
    "depends": ["l10n_br_account", "l10n_br_nfe"],
    "data": [
        "views/account_invoice_view.xml",
    ],
    "demo": [
    ],
    "installable": True,
    "auto_install": False,
    "maintainers": ["carlos"],
}
