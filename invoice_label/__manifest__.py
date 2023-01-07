# Copyright 2019 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Invoice labels",
    "version": "12.0.1.1.0",
    "author": "ATSti,Therp BV,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Account",
    "summary": "Print Invoice labels",
    "depends": [
        'account',
    ],
    "data": [
        "views/base_config_settings.xml",
        "reports/invoice_label.xml",
    ],
    "installable": True,
}
