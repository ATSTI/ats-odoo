# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons.l10n_br_fiscal.constants.fiscal import (
    TAX_DOMAIN_IBS,
    TAX_DOMAIN_CBS,
    TAX_DOMAIN_IBSCBS,
    TAX_DOMAIN_IBSUF,
    TAX_DOMAIN_IBSMUN
)

class FiscalDocumentIBSCBS(models.Model):
    _inherit = "l10n_br_fiscal.document"
    
    # BASES NOVAS PRECISAM QUE ESSES CAMPOS EXISTAM PARA PODEREM SER EXPORTAR PELO _export_field
    # ENTÃO, MESMO QUE NÃO SEJAM USADOS DIRETAMENTE, PRECISAM SER DECLARADOS AQUI, SE NÃO NÃO ENTRARAM NA EXPORTAÇÃO
    def _export_fields(self, xsd_fields, class_obj, export_dict):
        if class_obj._name == "nfe.40.total":
            import pudb;pu.db
            if "nfe40_IBSCBSTot" in class_obj._fields:
                vCBS = 0.0
                vIBSUF = 0.0
                vIBSMun = 0.0
                for line in self.move_ids.invoice_line_ids:
                    vCBS += line.amount_untaxed * (line.cbs_tax_id.percent_amount/100) if line.amount_untaxed else 0.00
                    vIBSUF += line.amount_untaxed * (line.ibsuf_tax_id.percent_amount/100) if line.amount_untaxed else 0.00
                    vIBSMun += line.amount_untaxed * (line.ibsmun_tax_id.percent_amount/100) if line.amount_untaxed else 0.00
                vIBS = vIBSUF + vIBSMun
                self.nfe40_vBCIBSCBS = vIBS + vCBS
                self.nfe40_vIBS = vIBS
                self.nfe40_vIBSUF = vIBSUF
                self.nfe40_vDif = 0.00 
                self.nfe40_vCredPres = 0.00
                self.nfe40_vDevTrib = 0.00
                self.nfe40_vIBSMun = vIBSMun
                self.nfe40_vCBS = vCBS
                self.nfe40_vCredPresCondSus = 0.00
            else:
                export_dict["nfe40_IBSCBSTot"] = None

        return super()._export_fields(xsd_fields, class_obj, export_dict)

    # SÓ VAI ENTRAR AQUI NO MOMENTO EM QUE OS CAMPOS EXISTEM, POR ALGUM MOTIVO, SE EU NÃO DECLARAR OS CAMPOS ACIMA, NÃO ENTRA AQUI
    def _export_field(self, xsd_field, class_obj, member_spec, export_value=None):
        if class_obj._name == "nfe.40.total":
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
        else:
            return None

    def _export_fields_nfe_40_gibscbs(self, xsd_fields, class_obj, export_dict):
        if not self.account_line_ids.ibscbs_cst_code:
            export_dict["vBC"] = None
            export_dict["vIBS"] = None
        else:
            export_dict["vBC"] = self.account_line_ids.amount_untaxed
            export_dict["vIBS"] = self.account_line_ids.amount_untaxed

    def _export_fields_nfe_40_gibsuf(self, xsd_fields, class_obj, export_dict):
        if not self.account_line_ids.ibsuf_tax_id:
            export_dict["pIBSUF"] = None
            export_dict["vIBSUF"] = None
        else:
            export_dict["pIBSUF"] = self.account_line_ids.ibsuf_tax_id.percent_amount
            export_dict["vIBSUF"] = self.account_line_ids.amount_untaxed * (self.account_line_ids.ibsuf_tax_id.percent_amount/100) if self.account_line_ids.amount_untaxed else 0.00

    def _export_fields_nfe_40_gibsmun(self, xsd_fields, class_obj, export_dict):
        if not self.account_line_ids.ibsmun_tax_id:
            export_dict["pIBSMun"] = None
            export_dict["vIBSMun"] = None
        else:
            export_dict["pIBSMun"] = self.account_line_ids.ibsmun_tax_id.percent_amount
            export_dict["vIBSMun"] = self.account_line_ids.amount_untaxed * (self.account_line_ids.ibsmun_tax_id.percent_amount/100) if self.account_line_ids.amount_untaxed else 0.00

    def _export_fields_nfe_40_gcbs(self, xsd_fields, class_obj, export_dict):
        if not self.account_line_ids.cbs_tax_id:
            export_dict["pCBS"] = None
            export_dict["vCBS"] = None
        else:
            export_dict["pCBS"] = self.account_line_ids.cbs_tax_id.percent_amount
            export_dict["vCBS"] = self.account_line_ids.amount_untaxed * (self.account_line_ids.cbs_tax_id.percent_amount/100) if self.account_line_ids.amount_untaxed else 0.00

class FiscalDocumentLineMixin(models.AbstractModel):
    _inherit = "l10n_br_fiscal.document.line.mixin"

    ibscbs_tax_id = fields.Many2one(
        comodel_name="l10n_br_fiscal.tax",
        string="Tax IBS/CBS",
        domain=[("tax_domain", "=", TAX_DOMAIN_IBSCBS)],
    )

    ibscbs_cst_id = fields.Many2one(
        comodel_name="l10n_br_fiscal.cst",
        string="CST IBS/CBS",
        domain="[('cst_type', '=', fiscal_operation_type),"
        "('tax_domain', '=', 'ibscbs')]",
    )

    ibscbs_cst_code = fields.Char(
        related="ibscbs_cst_id.code", string="IBS/CBS CST Code", store=True
    )
    # ibscbs_value = fields.Monetary(string="IBS/CBS Value")

    ibsuf_tax_id = fields.Many2one(
        comodel_name="l10n_br_fiscal.tax",
        string="Tax IBS UF",
        domain=[("tax_domain", "=", TAX_DOMAIN_IBSUF)],
    )

    ibsmun_tax_id = fields.Many2one(
        comodel_name="l10n_br_fiscal.tax",
        string="Tax IBS Mun",
        domain=[("tax_domain", "=", TAX_DOMAIN_IBSMUN)],
    )

    cbs_tax_id = fields.Many2one(
        comodel_name="l10n_br_fiscal.tax",
        string="Tax CBS",
        domain=[("tax_domain", "=", TAX_DOMAIN_CBS)],
    )