# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models



class FiscalDocumentMixinFields(models.AbstractModel):
    _inherit = "l10n_br_fiscal.document.mixin.fields"


    amount_icms_relief_value = fields.Monetary(
        string="ICMS Desoneracao",
        compute="_compute_amount",
        store=True,
    )
