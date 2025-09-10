# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models
from erpbrasil.base.misc import punctuation_rm


class FiscalDocumentCard(models.Model):
    _inherit = "l10n_br_fiscal.document"

    def _export_fields(self, xsd_fields, class_obj, export_dict):
        if class_obj._name == "nfe.40.imposto":
            for crd in self.move_ids.ibscbs_cst_id:
                ibscbs_vals =  {
                    "nfe40_CST": "001",
                    "nfe40_cClassTrib": "010002",
                }
                card = self.env["nfe.40.ibscbs"].create(card_vals)
                self.nfe40_detPag.nfe40_card = card

        return super()._export_fields(xsd_fields, class_obj, export_dict)
