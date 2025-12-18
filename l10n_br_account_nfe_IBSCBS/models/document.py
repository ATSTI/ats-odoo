# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

IBSCBS_SUB_TAGS = [
    "COFINSAliq",
    "COFINSQtde",
    "COFINSNT",
    "COFINSOutr",
]

IBSCBS_SELECTION = list(map(lambda tag: (f"nfe40_{tag}", tag), IBSCBS_SUB_TAGS))

class DocumentLine(models.Model):
    _inherit = "l10n_br_fiscal.document.line"

    def _export_fields_nfe_40_ibscbs(self, xsd_fields, class_obj, export_dict):
        if self.tax_classification_id:
            cst = self.tax_classification_id.code
            export_dict["CST"] = cst[:3]
            export_dict["cClassTrib"] = cst
            export_dict["cTipoTrib"] = "IBSCBS"
        else:
            return None

    def _export_fields_nfe_40_gibscbs(self, xsd_fields, class_obj, export_dict): 
        if self.tax_classification_id:
            export_dict["vBC"] = self.cbs_value + self.ibs_value
            export_dict["vIBS"] = self.ibs_value
            

    # def _export_fields_nfe_40_gibsuf(self, xsd_fields, class_obj, export_dict):
    #     if self.ibsuf_tax_id:
    #         export_dict["pIBSUF"] = self.ibsuf_aliquota
    #         export_dict["vIBSUF"] = self.ibsuf_value

    # def _export_fields_nfe_40_gibsmun(self, xsd_fields, class_obj, export_dict):
    #     if self.ibsmun_tax_id:
    #         export_dict["pIBSMun"] = self.ibsmun_aliquota
    #         export_dict["vIBSMun"] = self.ibsmun_value

    def _export_fields_nfe_40_gcbs(self, xsd_fields, class_obj, export_dict):
        if self.cbs_tax_id:
            export_dict["pCBS"] = self.cbs_percent
            export_dict["vCBS"] = self.cbs_value