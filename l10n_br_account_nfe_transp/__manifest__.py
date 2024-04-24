# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "NFe Transportadora/Volumes",
    "summary": "Dados Transportadora/Veiculo e Volumes adicionando pela fatura",
    "category": "Localisation",
    "license": "AGPL-3",
    "author": "ATSTi",
    "website": "https://github.com/OCA/l10n-brazil",
    "version": "14.0.1.0.2",
    "development_status": "Beta",
    "depends": [
        "l10n_br_nfe",
        "l10n_br_account",
        "l10n_br_delivery_nfe",
    ],
    "data": [
        "data/account_incoterms_data.xml",
        "security/ir.model.access.csv",
        "views/account_invoice_view.xml",
    ],
    "demo": [
    ],
    "installable": True,
    "auto_install": False,
}
