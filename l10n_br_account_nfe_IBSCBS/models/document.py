# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models
from erpbrasil.base.misc import punctuation_rm


class FiscalDocumentAgro(models.Model):
    _inherit = "l10n_br_fiscal.document"

    def _export_fields(self, xsd_fields, class_obj, export_dict):
        if class_obj._name == "nfe.40.total":
            import pudb;pu.db
            if "nfe40_IBSCBSTot" in class_obj._fields:
                if self.move_ids.ibscbs == True:
                    ibscbs_vals = {
                        "nfe40_vBCIBSCBS": 2260.00,
                        "nfe40_gIBS": self.env["nfe.40.gibs"].create({
                            "nfe40_gIBSUF": self.env["nfe.40.gibsuf"].create({
                                "nfe40_vDif": 0.00,
                                "nfe40_vDevTrib": 0.00,
                                "nfe40_vIBSUF": 2.26,
                            }).id,
                            "nfe40_gIBSMun": self.env["nfe.40.gibsmun"].create({
                                "nfe40_vDif": 0.00,
                                "nfe40_vDevTrib": 0.00,
                                "nfe40_vIBSMun": 0.00,
                            }).id,
                            "nfe40_vIBS": 2.26,
                            "nfe40_vCredPres": 0.00,
                            "nfe40_vCredPresCondSus": 0.00,
                        }).id,
                        "nfe40_gCBS": self.env["nfe.40.gcbs"].create({
                            "nfe40_vDif": 0.00,
                            "nfe40_vDevTrib": 0.00,
                            "nfe40_vCBS": 20.34,
                            "nfe40_vCredPres": 0.00,
                            "nfe40_vCredPresCondSus": 0.00,
                        }).id,
                    }
                    ibscbs = self.env["nfe.40.ibscbstot"].create(ibscbs_vals)
                    total = self.env["nfe.40.total"].browse(total_id)
                    total.nfe40_IBSCBSTot = ibscbs
                else:
                    self.nfe40_IBSCBSTot = False

        return super()._export_fields(xsd_fields, class_obj, export_dict)