# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models, _, fields
from odoo.exceptions import UserError

from odoo.addons.l10n_br_fiscal.constants.fiscal import (
    DOCUMENT_ISSUER_COMPANY,
)

class DocumentLineMixin(models.AbstractModel):
    _inherit = "l10n_br_fiscal.document.line.mixin"


    @api.depends(
        "partner_id",
        "fiscal_operation_line_id",
        "product_id",
        "ncm_id",
        "nbs_id",
        "nbm_id",
        "cest_id",
        "city_taxation_code_id",
        "national_taxation_code_id",
        "service_type_id",
        "ind_final",
    )
    def _compute_fiscal_tax_ids(self):
        for line in self:
            if line.fiscal_operation_line_id:
                mapping_result = line.fiscal_operation_line_id.map_fiscal_taxes(
                    company=line.company_id,
                    partner=line._get_fiscal_partner(),
                    product=line.product_id,
                    ncm=line.ncm_id,
                    nbm=line.nbm_id,
                    nbs=line.nbs_id,
                    cest=line.cest_id,
                    city_taxation_code=line.city_taxation_code_id,
                    national_taxation_code=line.national_taxation_code_id,
                    service_type=line.service_type_id,
                    ind_final=line.ind_final,
                )
                line.cfop_id = mapping_result["cfop"]
                line.ipi_guideline_id = mapping_result["ipi_guideline"]
                line.tax_classification_id = mapping_result["tax_classification"]
                if not line.cbenef_id and mapping_result.get("icms_tax_benefit_id"):
                    line.icms_tax_benefit_id = mapping_result["icms_tax_benefit_id"]

                if line._is_imported():
                    continue

                taxes = line.env["l10n_br_fiscal.tax"]
                for tax in mapping_result["taxes"].values():
                    taxes |= tax
                line.fiscal_tax_ids = taxes
