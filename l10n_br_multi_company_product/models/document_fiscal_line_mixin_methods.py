# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, api, models
from odoo.addons.l10n_br_fiscal.constants.fiscal import (
    TAX_DOMAIN_ICMS,
)
from odoo.addons.l10n_br_fiscal.constants.icms import (
    ICMS_ORIGIN_DEFAULT,
)

class FiscalDocumentLineMixin(models.AbstractModel):
    _inherit = "l10n_br_fiscal.document.line.mixin"

    @api.depends("product_id")
    def _compute_product_fiscal_fields(self):
        for line in self:
            super()._compute_product_fiscal_fields()
            if not line.product_id.icms_origin or not line.product_id.fiscal_type:
                prd_id = "product.template,{}".format(line.product_id.product_tmpl_id.id)
                prd = self.env["ir.property"].sudo().search([
                    ("type", "=", "selection"),
                    ("res_id", "=", prd_id),
                ])
                for p in prd:
                    if p.name == "fiscal_type" and not line.product_id.fiscal_type:
                        line.fiscal_type = p.value_text
                    if p.name == "icms_origin" and not line.product_id.icms_origin:
                        line.icms_origin = p.value_text