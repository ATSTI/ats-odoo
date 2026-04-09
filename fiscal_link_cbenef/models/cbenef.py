# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models, fields

class Cbenef(models.Model):
    _name = "l10n_br_fiscal.icms.cbenef"

    code = fields.Char(string="Código do Benefício Fiscal", required=True)
    description = fields.Char(string="Descrição do Benefício Fiscal")
    icms_cst_ids = fields.Many2many(
        "l10n_br_fiscal.cst",
        string="CSTs de ICMS",
    )
    name = fields.Char(compute="_compute_name", store=True)

    @api.depends("code", "description")
    def _compute_name(self):
        for rec in self:
            rec.name = f"{rec.code} - {rec.description}"