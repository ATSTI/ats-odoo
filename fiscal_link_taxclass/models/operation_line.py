# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models

from odoo.addons.l10n_br_fiscal.constants.fiscal import (
    CFOP_DESTINATION_EXPORT,
    TAX_DOMAIN_ICMS,
    TAX_DOMAIN_ISSQN,
    TAX_FRAMEWORK_NORMAL,
)

class OperationLine(models.Model):
    _inherit = "l10n_br_fiscal.operation.line"

    def map_fiscal_taxes(
        self,
        company,
        partner,
        product=None,
        fiscal_price=None,
        fiscal_quantity=None,
        ncm=None,
        nbm=None,
        nbs=None,
        cest=None,
        city_taxation_code=None,
        national_taxation_code=None,
        service_type=None,
        ind_final=None,
    ):
        mapping_result = {
            "taxes": {},
            "cfop": False,
            "ipi_guideline": self.env.ref("l10n_br_fiscal.tax_guideline_999"),
            "icms_tax_benefit_id": False,
            "tax_classification": False,
        }

        self.ensure_one()

        # Define CFOP
        mapping_result["cfop"] = self._get_cfop(company, partner)

        # Define Tax Classification
        mapping_result["tax_classification"] = self._get_tax_classification(company)

        # 1 Get Tax Defs from Company
        for tax_definition in company.tax_definition_ids.map_tax_definition(
            company,
            partner,
            product,
            ncm=ncm,
            nbm=nbm,
            nbs=nbs,
            cest=cest,
            city_taxation_code=city_taxation_code,
            national_taxation_code=national_taxation_code,
            service_type=service_type,
        ):
            self._build_mapping_result(mapping_result, tax_definition)

        # 2 From NCM
        if not ncm and product:
            ncm = product.ncm_id
        if ncm.tax_classification_id:
            mapping_result["tax_classification"] = ncm.tax_classification_id



        if company.tax_framework == TAX_FRAMEWORK_NORMAL:
            tax_ipi = ncm.tax_ipi_id
            tax_ii = ncm.tax_ii_id
            mapping_result["taxes"][tax_ipi.tax_domain] = tax_ipi

            if mapping_result["cfop"].destination == CFOP_DESTINATION_EXPORT:
                mapping_result["taxes"][tax_ii.tax_domain] = tax_ii

            # 3 From ICMS Regulation
            if company.icms_regulation_id:
                icms_taxes, icms_tax_defs = company.icms_regulation_id.map_tax(
                    company=company,
                    partner=partner,
                    product=product,
                    ncm=ncm,
                    nbm=nbm,
                    cest=cest,
                    operation_line=self,
                    ind_final=ind_final,
                )

                for tax_def in icms_tax_defs:
                    self._build_mapping_result_icms(mapping_result, tax_def)

                for tax in icms_taxes:
                    mapping_result["taxes"][tax.tax_domain] = tax

        # 4 From Operation Line
        for tax_definition in self.tax_definition_ids.map_tax_definition(
            company,
            partner,
            product,
            ncm=ncm,
            nbm=nbm,
            nbs=nbs,
            cest=cest,
            city_taxation_code=city_taxation_code,
            national_taxation_code=national_taxation_code,
            service_type=service_type,
        ):
            self._build_mapping_result(mapping_result, tax_definition)

        # 5 From CFOP
        for tax_definition in mapping_result[
            "cfop"
        ].tax_definition_ids.map_tax_definition(
            company,
            partner,
            product,
            ncm=ncm,
            nbm=nbm,
            nbs=nbs,
            cest=cest,
            city_taxation_code=city_taxation_code,
            national_taxation_code=national_taxation_code,
            service_type=service_type,
        ):
            self._build_mapping_result(mapping_result, tax_definition)
        if mapping_result["cfop"].tax_classification_id:
            if mapping_result["cfop"].tax_classification_id.code == "000000":
                mapping_result["tax_classification"] = None
            else:
                mapping_result["tax_classification"] = mapping_result[
                    "cfop"
                ].tax_classification_id

        # 6 From Partner Profile
        for (
            tax_definition
        ) in partner.fiscal_profile_id.tax_definition_ids.map_tax_definition(
            company,
            partner,
            product,
            ncm=ncm,
            nbm=nbm,
            nbs=nbs,
            cest=cest,
            city_taxation_code=city_taxation_code,
            national_taxation_code=national_taxation_code,
            service_type=service_type,
        ):
            self._build_mapping_result(mapping_result, tax_definition)

        if product.tax_icms_or_issqn == TAX_DOMAIN_ICMS:
            mapping_result["taxes"].pop(TAX_DOMAIN_ISSQN, None)
        elif product.tax_icms_or_issqn == TAX_DOMAIN_ISSQN:
            mapping_result["taxes"].pop(TAX_DOMAIN_ICMS, None)
        else:
            mapping_result["taxes"].pop(TAX_DOMAIN_ICMS, None)
            mapping_result["taxes"].pop(TAX_DOMAIN_ISSQN, None)

        if mapping_result["tax_classification"]:
            mapping_result["taxes"][
                mapping_result["tax_classification"].tax_cbs_id.tax_domain
            ] = mapping_result["tax_classification"].tax_cbs_id

            mapping_result["taxes"][
                mapping_result["tax_classification"].tax_ibs_id.tax_domain
            ] = mapping_result["tax_classification"].tax_ibs_id

        return mapping_result
    
