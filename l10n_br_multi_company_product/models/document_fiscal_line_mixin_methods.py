# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, api, models


class FiscalDocumentLineMixinMethods(models.AbstractModel):
    _inherit = "l10n_br_fiscal.document.line.mixin.methods"

    @api.onchange("product_id")
    def _onchange_product_id_fiscal(self):
        super()._onchange_product_id_fiscal()
        if self.product_id:
            if not self.product_id.icms_origin or not self.product_id.fiscal_type:
                prd_id = "product.template,{}".format(self.product_id.product_tmpl_id.id)
                prd = self.env["ir.property"].sudo().search([
                    ("type", "=", "selection"),
                    ("res_id", "=", prd_id),
                ])
                for p in prd:
                    if p.name == "fiscal_type" and not self.product_id.fiscal_type:
                        self.fiscal_type = p.value_text
                    if p.name == "icms_origin" and not self.product_id.icms_origin:
                        self.icms_origin = p.value_text
                self._get_product_price()
                self._onchange_fiscal_operation_id()