# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account NFe DI/DetExport",
    "summary": "Adicionado campos para Detalhes Importação/Exportação",
    "category": "Localisation",
    "license": "AGPL-3",
    "author": "Engenere," "Akretion," "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-brazil",
    "version": "14.0.1.0.0",
    "development_status": "Alpha",
    "depends": [
        "l10n_br_fiscal",
        "l10n_br_nfe",
        "l10n_br_account",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/account_invoice_view.xml",
        "wizard/create_di_view.xml",
    ],
    "demo": [
    ],
    "installable": True,
    "auto_install": True,
}
