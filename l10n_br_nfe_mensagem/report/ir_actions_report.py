# Copyright 2024 Engenere.one
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from brazilfiscalreport.danfe import Danfe, DanfeConfig, InvoiceDisplay, Margins, FontSize
from odoo import _, api, models

_logger = logging.getLogger(__name__)


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    @api.model
    def _get_danfe_config(self, tmpLogo, company):
        margins = Margins(
            top=company.danfe_margin_top,
            right=company.danfe_margin_right,
            bottom=company.danfe_margin_bottom,
            left=company.danfe_margin_left,
        )
        danfe_config = {
            "logo": tmpLogo,
            "margins": margins,
        }
        if company.danfe_font_size:
            danfe_config['font_size'] = FontSize.BIG
        if company.danfe_invoice_display == "duplicates_only":
            danfe_config["invoice_display"] = InvoiceDisplay.DUPLICATES_ONLY
        return DanfeConfig(**danfe_config)


