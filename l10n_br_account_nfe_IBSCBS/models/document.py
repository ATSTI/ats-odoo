# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models
from erpbrasil.base.misc import punctuation_rm


# class FiscalDocumentIBSCBS(models.Model):
#     _inherit = "l10n_br_fiscal.document"

#     def _export_fields(self, xsd_fields, class_obj, export_dict):
#         if class_obj._name == "nfe.40.total":
#             if "nfe40_IBSCBSTot" in class_obj._fields:
#                     print('oi')
#                 else:
#                     export_dict["nfe40_IBSCBSTot"] = None

#         return super()._export_fields(xsd_fields, class_obj, export_dict)
    

class DocumentLine(models.Model):
    _inherit = "l10n_br_fiscal.document.line"

    def _export_fields_nfe_40_ibscbs(self, xsd_fields, class_obj, export_dict):
        if self.document_id.move_ids.ibscbs:
            export_dict["CST"] = self.document_id.move_ids.cst_ibscbs
            export_dict["cClassTrib"] = "000002"

    def _export_fields_nfe_40_gibscbs(self, xsd_fields, class_obj, export_dict):
        if self.document_id.move_ids.ibscbs:
            export_dict["vBC"] = 1.00        

    def _export_fields_nfe_40_gibsuf(self, xsd_fields, class_obj, export_dict):
        if self.document_id.move_ids.ibscbs:
            export_dict["pIBSUF"] = 1.00
            export_dict["vIBSUF"] = 1.00

    def _export_fields_nfe_40_gibsmun(self, xsd_fields, class_obj, export_dict):
        if self.document_id.move_ids.ibscbs:
            export_dict["pIBSMun"] = 1.00
            export_dict["vIBSMun"] = 1.00

    def _export_fields_nfe_40_gcbs(self, xsd_fields, class_obj, export_dict):
        if self.document_id.move_ids.ibscbs:
            export_dict["pCBS"] = 1.00
            export_dict["vCBS"] = 1.00

    # IBSCBS Total
    def _export_fields_nfe_40_ibscbstot(self, xsd_fields, class_obj, export_dict):
        if self.document_id.move_ids.ibscbs:
            export_dict["vBCIBSCBS"] = 2260.0

    def _export_fields_nfe_40_gibs(self, xsd_fields, class_obj, export_dict):
        if self.document_id.move_ids.ibscbs:
            export_dict["vIBS"] = 2.26
            export_dict["vCredPres"] = 0.0

    def _export_fields_nfe_40_tgibsuf(self, xsd_fields, class_obj, export_dict):
        if self.document_id.move_ids.ibscbs:
            export_dict["vDif"] = 1.00
            export_dict["vIBSUF"] = 1.00
            export_dict["vDevTrib"] = 0.00

    def _export_fields_nfe_40_tgibsmun(self, xsd_fields, class_obj, export_dict):
        if self.document_id.move_ids.ibscbs:
            export_dict["vDif"] = 1.00
            export_dict["vIBSMun"] = 1.00
            export_dict["vDevTrib"] = 0.00
    
    def _export_fields_nfe_40_tgcbs(self, xsd_fields, class_obj, export_dict):
        if self.document_id.move_ids.ibscbs:
            export_dict["vCBS"] = 1.00
            export_dict["vCredPres"] = 0.0
            export_dict["vCredPresCondSus"] = 0.0