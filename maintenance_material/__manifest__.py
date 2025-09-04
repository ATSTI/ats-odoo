# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).
{
    "name": "Maintenance Material",
    "summary": "Adiciona materiais na OM",
    "version": "16.0",
    "category": "Maintenance",
    "author": "ATSTi,Odoo Community Association (OCA)",
    "website": "",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["maintenance", "product"],
    "data": [
        "security/ir.model.access.csv",
        "views/maintenance_view.xml"
    ],
}
