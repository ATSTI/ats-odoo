# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "NFe Informações Agronomicas",
    "summary": "AGRONEGÓCIO - Adiciona campos de informações agronômicas na NFe",
    "category": "Localisation",
    "license": "AGPL-3",
    "author": "ATSTi",
    "website": "https://github.com/OCA/l10n-brazil",
    "version": "12.0.1.0.2",
    "development_status": "Beta",
    "depends": [
        "br_nfe",
        'br_account_einvoice',
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/account_invoice_view.xml",
    ],
    "demo": [
    ],
    "installable": True,
    "auto_install": False,
}
