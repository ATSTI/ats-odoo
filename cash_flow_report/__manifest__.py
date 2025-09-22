# Author: Carlos Silveira
# Copyright 2022 ATSTi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Cash Flow Reports",
    "version": "16.0",
    "category": "Reporting",
    "summary": "Financial Reports",
    "author": "ATSTi Soluções",
    "website": "",
    "depends": ["account", "date_range", "report_xlsx"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/cash_flow_wizard_view.xml",
        "menuitems.xml",
        "reports.xml",
        "report/templates/layouts.xml",
        "report/templates/cash_flow.xml",
        "view/report_template.xml",
        "view/report_cash_flow.xml",
    ],
    "qweb": ["static/src/xml/report.xml"],
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "AGPL-3",
}
