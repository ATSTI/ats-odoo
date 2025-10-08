# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models
from erpbrasil.base.misc import punctuation_rm


class FiscalDocumentIBSCBS(models.Model):
    _inherit = "l10n_br_fiscal.document"
    
    def _export_field(self, xsd_field, class_obj, member_spec, export_value=None):
            vCBS = 0.0
            vIBSUF = 0.0
            vIBSMun = 0.0
            for line in self.move_ids.invoice_line_ids:
                vCBS += line.amount_untaxed * (line.cbs_tax_id.percent_amount/100) if line.amount_untaxed else 0.00
                vIBSUF += line.amount_untaxed * (line.ibsuf_tax_id.percent_amount/100) if line.amount_untaxed else 0.00
                vIBSMun += line.amount_untaxed * (line.ibsmun_tax_id.percent_amount/100) if line.amount_untaxed else 0.00
            vIBS = vIBSUF + vIBSMun
            simulated_values = {
                "nfe40_vIBS": vIBS,
                "nfe40_vIBSUF": vIBSUF,
                "nfe40_vIBSMun": vIBSMun,
                "nfe40_vCBS": vCBS,
                "nfe40_vBCIBSCBS": vIBS + vCBS,
            }

            if xsd_field in simulated_values and getattr(self, "move_ids", None):
                export_value = simulated_values[xsd_field]

            return super()._export_field(xsd_field, class_obj, member_spec, export_value)

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
