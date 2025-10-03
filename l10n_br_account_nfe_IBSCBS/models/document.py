# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models
from erpbrasil.base.misc import punctuation_rm


class FiscalDocumentIBSCBS(models.Model):
    _inherit = "l10n_br_fiscal.document"

    def _export_fields(self, xsd_fields, class_obj, export_dict):
        if class_obj._name == "nfe.40.total":
            import pudb;pu.db
            if "nfe40_IBSCBSTot" in class_obj._fields:
                if self.move_ids.ibscbs:
                    # ibscbs_vals = {
                    #     "nfe40_vBCIBSCBS": 2260.00,
                    #     "nfe40_gIBS": {
                    #         "nfe40_gIBSUF": {
                    #             "nfe40_vDif": 0.00,
                    #             "nfe40_vDevTrib": 0.00,
                    #             "nfe40_vIBSUF": 2.26,
                    #         },
                    #         "nfe40_gIBSMun": {
                    #             "nfe40_vDif": 0.00,
                    #             "nfe40_vDevTrib": 0.00,
                    #             "nfe40_vIBSMun": 0.00,
                    #         },
                    #         "nfe40_vIBS": 2.26,
                    #         "nfe40_vCredPres": 0.00,
                    #         "nfe40_vCredPresCondSus": 0.00,
                    #     },
                    #     "nfe40_gCBS": {
                    #         "nfe40_vDif": 0.00,
                    #         "nfe40_vDevTrib": 0.00,
                    #         "nfe40_vCBS": 20.34,
                    #         "nfe40_vCredPres": 0.00,
                    #         "nfe40_vCredPresCondSus": 0.00,
                    #     },
                    # }
                    self.nfe40_IBSCBSTot = self.env['nfe.40.ibscbstot'].create({})
                else:
                    export_dict["nfe40_IBSCBSTot"] = None

        return super()._export_fields(xsd_fields, class_obj, export_dict)