# Copyright (C) 2017-19 ForgeFlow S.L. (https://www.forgeflow.com).
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "Lead Contact",
    "version": "15.0.1.0.1",
    "category": "Customer Relationship Management",
    "license": "LGPL-3",
    "summary": "Adds a lead line in the lead/opportunity model " "in odoo",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/crm",
    "depends": ["crm", "product"],
    "data": [
        "views/crm_lead_views.xml",
    ],
    "installable": True,
    "auto_install": False,
}
