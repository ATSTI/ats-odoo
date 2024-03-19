# -*- coding: utf-8 -*-
# Copyright 2022 Carlos - ATSti Soluções
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Lembrete do certificado",
    "version": "14.0.0.0.0",
    "development_status": "Alfa",
    "category": "Invoice",
    "summary": "Mail certificate cron",
    "author": "ATSti",
    "license": "AGPL-3",
    "depends": [
        "web_notify",
        "l10n_br_fiscal_certificate",
        ],
    "data": [
        # "security/ir.model.access.csv",
        "data/ir_cron.xml",
        "data/mail_template.xml",
    ],
    "installable": True,
    "auto_install": False
}