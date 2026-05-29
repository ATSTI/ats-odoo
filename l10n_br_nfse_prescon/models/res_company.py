# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    provedor_nfse = fields.Selection(
        selection_add=[
            ("prescon", "Prescon"),
        ]
    )

    prescon_production_token = fields.Char(
        string="Prescon Production Token",
    )

    prescon_code = fields.Char(
        string="Prescon Code",
    )
