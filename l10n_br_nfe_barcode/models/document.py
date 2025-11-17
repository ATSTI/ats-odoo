# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields
from erpbrasil.base.misc import punctuation_rm


class FiscalDocumentLine(models.Model):
    _inherit = "l10n_br_fiscal.document.line"

    nfe40_cEAN = fields.Char("NFe40 Código de Barras")
    nfe40_cEANTrib = fields.Char("NFe40 Código de Barras Tributável")

    def _export_fields_nfe_40_prod(self, xsd_fields, class_obj, export_dict):
        nfe40_cProd = self.product_id.default_code or self.nfe40_cProd or ""
        export_dict["cProd"] = nfe40_cProd

        nfe40_xProd = (
            self.product_id.with_context(display_default_code=False).display_name
            or self.name
            or ""
        )
        export_dict["xProd"] = nfe40_xProd[:120].replace("\n", " ").strip()

        if self.product_id and len(punctuation_rm(self.product_id.barcode or "")) < 12:
            export_dict["cEAN"] = export_dict["cEANTrib"] = "SEM GTIN"
            self.nfe40_cEAN = self.nfe40_cEANTrib = "SEM GTIN"
        else:
            nfe40_cEAN = self.product_id.barcode or "SEM GTIN"
            export_dict["cEAN"] = export_dict["cEANTrib"] = nfe40_cEAN
            self.nfe40_cEAN = self.nfe40_cEANTrib = nfe40_cEAN
