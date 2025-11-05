# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons.l10n_br_fiscal.constants.fiscal import (
    TAX_DOMAIN_IBS,
    TAX_DOMAIN_CBS,
    TAX_DOMAIN_IBSCBS,
    TAX_DOMAIN_IBSUF,
    TAX_DOMAIN_IBSMUN
)
# from odoo.addons.l10n_br_fiscal.models.tax import TAX_DICT_VALUES

FISCAL_TAX_ID_FIELDS = [
    "cofins_tax_id",
    "cofins_wh_tax_id",
    "cofinsst_tax_id",
    "csll_tax_id",
    "csll_wh_tax_id",
    "icms_tax_id",
    "icmsfcp_tax_id",
    "icmssn_tax_id",
    "icmsst_tax_id",
    "icmsfcpst_tax_id",
    "ii_tax_id",
    "inss_tax_id",
    "inss_wh_tax_id",
    "ipi_tax_id",
    "irpj_tax_id",
    "irpj_wh_tax_id",
    "issqn_tax_id",
    "issqn_wh_tax_id",
    "pis_tax_id",
    "pis_wh_tax_id",
    "pisst_tax_id",
    "ibscbs_tax_id",
    "ibsuf_tax_id",
    "ibsmun_tax_id",
    "cbs_tax_id",
]
TAX_DICT_VALUES = {
    "name": False,
    "fiscal_tax_id": False,
    "tax_include": False,
    "tax_withholding": False,
    "tax_domain": False,
    "cst_id": False,
    "cst_code": False,
    "base_type": "percent",
    "base": 0.00,
    "base_reduction": 0.00,
    "percent_amount": 0.00,
    "percent_reduction": 0.00,
    "value_amount": 0.00,
    "uot_id": False,
    "tax_value": 0.00,
    "add_to_base": 0.00,
    "remove_from_base": 0.00,
    "compute_reduction": True,
    "compute_with_tax_value": False,
    "icms_dest_base": 0.00,
    "icms_origin_value": 0.00,
    "icms_dest_value": 0.00,
    "ibsuf_value": 0.00,
    "ibsuf_aliquota": 0.00,
}


class FiscalDocumentIBSCBS(models.Model):
    _inherit = "l10n_br_fiscal.document"       

    # BASES NOVAS PRECISAM QUE ESSES CAMPOS EXISTAM PARA PODEREM SER EXPORTAR PELO _export_field
    # ENTÃO, MESMO QUE NÃO SEJAM USADOS DIRETAMENTE, PRECISAM SER DECLARADOS AQUI, SE NÃO NÃO ENTRARAM NA EXPORTAÇÃO
    def _export_fields(self, xsd_fields, class_obj, export_dict):
        if class_obj._name == "nfe.40.total":
            
            if "nfe40_IBSCBSTot" in class_obj._fields:
                vCBS = 0.0
                vIBSUF = 0.0
                vIBSMun = 0.0
                vIBSCBS = 0.0
                for line in self.fiscal_line_ids:
                    cst = line.ibscbs_cst_code or line.ibscbs_tax_id.cst_out_id.code
                    vCBS += line.cbs_value
                    vIBSUF += line.ibsuf_value
                    vIBSMun += line.ibsmun_value
                    vIBSCBS += line.ibscbs_base
                    if cst == '4114':
                        vIBSCBS = 0.0
                    #  or self.fiscal_operation_id.fiscal_type in ('return_in', 'return_out', 'other')
                vIBS = vIBSUF + vIBSMun
                self.nfe40_vBCIBSCBS = vIBSCBS
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


class DocumentLine(models.Model):
    _inherit = "l10n_br_fiscal.document.line"

    def _export_fields_nfe_40_ibscbs(self, xsd_fields, class_obj, export_dict):
        if self.ibscbs_tax_id or self.ibscbs_cst_code:
            cst = self.ibscbs_cst_code or self.ibscbs_tax_id.cst_out_id.code
            # TODO fazer uma lista dos CSTs ques os grupos nao precisam ser informados como o 410
            #  or self.fiscal_operation_id.fiscal_type in ('return_in', 'return_out', 'other')
            if cst == '4114':
                xsd_fields.remove("nfe40_gIBSCBS")
            export_dict["CST"] = cst[:2] + '0'
            export_dict["cClassTrib"] = cst[:2] + '0' + cst[2:4].zfill(3)
        else:
            return None

    def _export_fields_nfe_40_gibscbs(self, xsd_fields, class_obj, export_dict):        
        if self.cbs_tax_id:
            export_dict["vBC"] = self.ibscbs_base
            export_dict["vIBS"] = self.ibsuf_value + self.ibsmun_value
            

    def _export_fields_nfe_40_gibsuf(self, xsd_fields, class_obj, export_dict):
        if self.ibsuf_tax_id:
            export_dict["pIBSUF"] = self.ibsuf_aliquota
            export_dict["vIBSUF"] = self.ibsuf_value

    def _export_fields_nfe_40_gibsmun(self, xsd_fields, class_obj, export_dict):
        if self.ibsmun_tax_id:
            export_dict["pIBSMun"] = self.ibsmun_aliquota
            export_dict["vIBSMun"] = self.ibsmun_value

    def _export_fields_nfe_40_gcbs(self, xsd_fields, class_obj, export_dict):
        if self.cbs_tax_id:
            export_dict["pCBS"] = self.cbs_aliquota
            export_dict["vCBS"] = self.cbs_value

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
    ibscbs_base = fields.Monetary(string="Base IBS/CBS")
    ibsuf_aliquota = fields.Monetary(string="Aliquota IBSUF")
    ibsmun_aliquota = fields.Monetary(string="Aliquota IBSMun")
    ibs_reduction  = fields.Monetary(string="Perc. redução IBS")
    ibsuf_value = fields.Monetary(string="Valor IBS/UF")
    ibsmun_value = fields.Monetary(string="Valor IBS/Mun")
    cbs_aliquota = fields.Monetary(string="Aliquota CBS")
    cbs_reduction = fields.Monetary(string="Perc. redução CBS")
    cbs_value = fields.Monetary(string="Valor CBS")


class FiscalDocumentLineMixinMethods(models.AbstractModel):
    _inherit = "l10n_br_fiscal.document.line.mixin.methods"

    def _prepare_fields_ibscbs(self, tax_dict):
        self.ensure_one()
        # cst_id = self.ibscbs_tax_id.cst_out_id.id
        pRedIBS = self.ibscbs_tax_id.percent_reduction
        base_bs = self.amount_untaxed - (self.amount_untaxed * (pRedIBS/100) if pRedIBS else 0.00)
        return {"ibscbs_base": base_bs}

    def _prepare_fields_ibsuf(self, tax_dict):
        self.ensure_one()
        if not self.ibsuf_tax_id:
            return {}
        pRedIBS = self.ibsuf_tax_id.percent_reduction
        ibsuf_aliquota = self.ibsuf_tax_id.percent_amount if self.ibsuf_tax_id else 0.00
        base_bs = self.amount_untaxed - (self.amount_untaxed * (pRedIBS/100) if pRedIBS else 0.00)
        ibsuf_value = base_bs * (ibsuf_aliquota/100) if self.ibsuf_tax_id else 0.00
        return {           
            "ibsuf_aliquota": ibsuf_aliquota,
            "ibsuf_value": ibsuf_value,
            "ibs_reduction": pRedIBS,
        }

    def _prepare_fields_ibsmun(self, tax_dict):
        self.ensure_one()
        if not self.ibsuf_tax_id:
            return {}
        pRedIBS = self.ibsmun_tax_id.percent_reduction
        ibsmun_aliquota = self.ibsmun_tax_id.percent_amount if self.ibsmun_tax_id else 0.00
        base_bs = self.amount_untaxed - (self.amount_untaxed * (pRedIBS/100) if pRedIBS else 0.00)
        ibsmun_value = base_bs * (ibsmun_aliquota/100) if self.ibsuf_tax_id else 0.00
        return {           
            "ibsmun_aliquota": ibsmun_aliquota,
            "ibsmun_value": ibsmun_value,
        }

    def _prepare_fields_cbs(self, tax_dict):
        self.ensure_one()
        if not self.cbs_tax_id:
            return {}
        pRedCBS = self.cbs_tax_id.percent_reduction
        cbs_aliquota = self.cbs_tax_id.percent_amount if self.cbs_tax_id else 0.00
        base_bs = self.amount_untaxed - (self.amount_untaxed * (pRedCBS/100) if pRedCBS else 0.00)
        cbs_value = base_bs * (cbs_aliquota/100) if self.cbs_tax_id else 0.00
        return {           
            "cbs_aliquota": cbs_aliquota,
            "cbs_value": cbs_value,
            "cbs_reduction": pRedCBS,
        }

    def _remove_all_fiscal_tax_ids(self):
        for line in self:
            to_update = {"fiscal_tax_ids": False}
            for fiscal_tax_field in FISCAL_TAX_ID_FIELDS:
                to_update[fiscal_tax_field] = False
            tax_methods = [
                self._prepare_fields_issqn,
                self._prepare_fields_csll,
                self._prepare_fields_irpj,
                self._prepare_fields_inss,
                self._prepare_fields_icms,
                self._prepare_fields_icmsfcp,
                self._prepare_fields_icmsfcpst,
                self._prepare_fields_icmsst,
                self._prepare_fields_icmssn,
                self._prepare_fields_ipi,
                self._prepare_fields_ii,
                self._prepare_fields_pis,
                self._prepare_fields_pisst,
                self._prepare_fields_cofins,
                self._prepare_fields_cofinsst,
                self._prepare_fields_issqn_wh,
                self._prepare_fields_pis_wh,
                self._prepare_fields_cofins_wh,
                self._prepare_fields_csll_wh,
                self._prepare_fields_irpj_wh,
                self._prepare_fields_inss_wh,
                self._prepare_fields_ibscbs,
                self._prepare_fields_ibsuf,
                self._prepare_fields_ibsmun,
                self._prepare_fields_cbs,
            ]
            for method in tax_methods:
                prepared_fields = method(TAX_DICT_VALUES)
                if prepared_fields:
                    to_update.update(prepared_fields)
            # Update all fields at once
            line.update(to_update)
