# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models


from odoo.addons.l10n_br_fiscal.constants.icms import (
    ICMS_CST_RELIEF,
)

class Tax(models.Model):
    _inherit = "l10n_br_fiscal.tax"

    @api.model
    def _compute_icms(self, tax, taxes_dict, **kwargs):
        result = super()._compute_icms(tax, taxes_dict, **kwargs)
        tax_dict = taxes_dict.get(tax.tax_domain)
        cst = kwargs.get("icms_cst_id", self.env["l10n_br_fiscal.cst"])

        if kwargs.get("icms_relief_id") and cst["code"] in ICMS_CST_RELIEF:
            icms_base = kwargs.get("price_unit", 0.00) * kwargs.get("quantity", 0.00)
            icms_percent = tax_dict.get("percent_amount", 0.00) / 100
            icms_reduction = tax_dict.get("percent_reduction", 0.00) / 100
            if cst["code"] in ["30", "40"]:
                icms_relief = icms_base * icms_percent
                tax_dict.update({"icms_relief": icms_relief})
            elif cst["code"] in ["20", "70"] and kwargs.get("icms_relief_id").code == "3":
                # quando icms_relief_id == "3 - Produtor Agropecuário", valor desoneracao = valor icms
                icms_relief = (icms_base * (1 - icms_reduction)) * icms_percent
                tax_dict.update({"icms_relief": icms_relief})
            elif cst["code"] in ["20", "70"]:
                #icms_relief = (
                #    icms_base
                #    * (1 - (icms_percent * (1 - icms_reduction)))
                #    / (1 - icms_percent)
                #    - icms_base
                #)
                icms_normal = icms_base * icms_percent
                icms_reduzido = (icms_base * (1 - icms_reduction)) * icms_percent
                icms_relief = icms_normal - icms_reduzido
                tax_dict.update({"icms_relief": icms_relief})
            else:
                icms_relief = (icms_base / (1 - icms_percent)) * icms_percent
                tax_dict.update({"icms_relief": icms_relief})
        else:
            tax_dict.update({"icms_relief": 0})
        return result
    