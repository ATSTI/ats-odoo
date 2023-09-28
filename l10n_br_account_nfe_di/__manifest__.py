# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "ATSTO-Account NFe DI/DetExport",
    "summary": "ATS-Adicionado campos para Detalhes Importação/Exportação",
    "category": "Localisation",
    "license": "AGPL-3",
    "author": "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-brazil",
    "version": "14.0.1.0.2",
    "development_status": "Beta",
    "depends": [
        "l10n_br_fiscal",
        "l10n_br_nfe",
        "l10n_br_account",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/account_invoice_view.xml",
        "wizard/create_di_view.xml",
        "wizard/create_detexp_view.xml",
    ],
    "demo": [
    ],
    "installable": True,
    "auto_install": False,
}
