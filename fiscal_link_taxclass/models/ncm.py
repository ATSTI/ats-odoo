# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models



class Ncm(models.Model):
    _inherit = "l10n_br_fiscal.ncm"

    tax_classification_id = fields.Many2one(
        comodel_name="l10n_br_fiscal.tax.classification",
        string="Tax Classification",
    )
