# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models
from erpbrasil.base.misc import punctuation_rm


class FiscalDocumentIBSCBS(models.Model):
    _inherit = "l10n_br_fiscal.document"

    def _export_fields(self, xsd_fields, class_obj, export_dict):
        if class_obj._name == "nfe.40.total":
            if "nfe40_IBSCBSTot" in class_obj._fields:
                if self.move_ids.ibscbs:
                    self.nfe40_vBCIBSCBS = 2260.00
                    self.nfe40_vIBS = 2.26
                    self.nfe40_vIBSUF = 1.00
                    self.nfe40_vDif = 1.00 
                    self.nfe40_vCredPres = 1.00
                    self.nfe40_vDevTrib = 1.00
                    self.nfe40_vIBSMun = 1.00
                    self.nfe40_vCBS = 20.34
                    self.nfe40_vCredPresCondSus = 1.00
                else:
                    export_dict["nfe40_IBSCBSTot"] = None

        return super()._export_fields(xsd_fields, class_obj, export_dict)
    

class DocumentLine(models.Model):
    _inherit = "l10n_br_fiscal.document.line"

    def _export_fields_nfe_40_ibscbs(self, xsd_fields, class_obj, export_dict):
        if self.account_line_ids.ibscbs_cst_code:
            export_dict["CST"] = self.account_line_ids.ibscbs_cst_code[:3]
            export_dict["cClassTrib"] = self.account_line_ids.ibscbs_cst_code[:3] + self.account_line_ids.ibscbs_cst_code[3:4].zfill(3)

    def _export_fields_nfe_40_gibscbs(self, xsd_fields, class_obj, export_dict):
        export_dict["vBC"] = self.account_line_ids.amount_untaxed
        export_dict["vIBS"] = self.account_line_ids.amount_untaxed

    def _export_fields_nfe_40_gibsuf(self, xsd_fields, class_obj, export_dict):
        export_dict["pIBSUF"] = self.account_line_ids.ibsuf_tax_id.percent_amount
        export_dict["vIBSUF"] = self.account_line_ids.amount_untaxed * (self.account_line_ids.ibsuf_tax_id.percent_amount/100) if self.account_line_ids.amount_untaxed else 0.00

    def _export_fields_nfe_40_gibsmun(self, xsd_fields, class_obj, export_dict):
        export_dict["pIBSMun"] = self.account_line_ids.ibsmun_tax_id.percent_amount
        export_dict["vIBSMun"] = self.account_line_ids.amount_untaxed * (self.account_line_ids.ibsmun_tax_id.percent_amount/100) if self.account_line_ids.amount_untaxed else 0.00

    def _export_fields_nfe_40_gcbs(self, xsd_fields, class_obj, export_dict):
        if self.document_id.move_ids.ibscbs:
            export_dict["pCBS"] = self.account_line_ids.cbs_tax_id.percent_amount
            export_dict["vCBS"] = self.account_line_ids.amount_untaxed * (self.account_line_ids.cbs_tax_id.percent_amount/100) if self.account_line_ids.amount_untaxed else 0.00
