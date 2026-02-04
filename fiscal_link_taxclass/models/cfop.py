# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models


class Cfop(models.Model):
    _inherit = "l10n_br_fiscal.cfop"

    tax_classification_id = fields.Many2one(
        comodel_name="l10n_br_fiscal.tax.classification",
        string="Tax Classification",
    )    