# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Brazilian Localization Accounts Patch",
    "category": "Localisation",
    "description": """
        Quando tem icms de desoneração e com código 03-Alívio do ICMS, desconta o valor do ICMS do total da nota.
    """,
    "license": "AGPL-3",
    "author": "ATSTi,Odoo Community Association (OCA)",
    "website": "",
    "version": "16.0",
    "depends": [
        "l10n_br_fiscal",
        "l10n_br_nfe",
        "l10n_br_nfe_spec",
        "spec_driven_model",
    ],
    "data": [
        "views/document_view.xml",
    ],
    "demo": [
    ],
    "installable": True,
    "auto_install": False,
    "maintainers": ["carlos"],
}
