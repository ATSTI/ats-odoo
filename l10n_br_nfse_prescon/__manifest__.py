# Copyright 2026 ATS TI Soluções
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "NFS-e (PRESCON)",
    "summary": """
        NFS-e (PRESCON)
        usado como base o codigo do modulo l10n_br_nfse_focus(OCA/l10n-brazil)
        """,
    "version": "18.0.3.1.0",
    "license": "AGPL-3",
    "author": "ATS TI Soluções",
    "maintainers": [
        "crsilveira",
    ],
    "website": "https://github.com/ATSTI/ats-odoo",
    "development_status": "Beta",
    "depends": [
        "l10n_br_fiscal_edi",
        "l10n_br_nfse",
    ],
    "data": [
        "views/res_company.xml",
        "data/l10n_br_nfse_prescon_cron.xml",
        "wizards/document_cancel_wizard.xml",
    ],
}
