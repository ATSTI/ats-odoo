# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models


class DocumentNfe(models.Model):
    _inherit = "l10n_br_fiscal.document"

    nfe40_vICMSDeson = fields.Monetary(related="amount_icms_relief_value")

    @api.depends(
        "fiscal_line_ids.estimate_tax",
        "fiscal_line_ids.price_gross",
        "fiscal_line_ids.amount_untaxed",
        "fiscal_line_ids.amount_tax",
        "fiscal_line_ids.amount_taxed",
        "fiscal_line_ids.amount_total",
        "fiscal_line_ids.financial_total",
        "fiscal_line_ids.financial_total_gross",
        "fiscal_line_ids.financial_discount_value",
        "fiscal_line_ids.amount_tax_included",
        "fiscal_line_ids.amount_tax_not_included",
        "fiscal_line_ids.amount_tax_withholding",
        "fiscal_line_ids.icms_relief_value",
    )
    def _compute_amount(self):
        return super()._compute_amount()    