# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models, fields


class ProductFiscalClassification(models.Model):
    _inherit = 'product.fiscal.classification'

    cbenef_id = fields.Many2one(
        "l10n_br_fiscal.icms.cbenef",
        string="Benefício Fiscal (CST)",
    )
