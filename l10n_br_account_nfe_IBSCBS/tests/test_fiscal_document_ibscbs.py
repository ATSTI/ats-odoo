# Copyright 2020 KMEE INFORMATICA LTDA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase

from odoo.addons.l10n_br_fiscal.constants.fiscal import (
    PROCESSADOR_NENHUM,
    PROCESSADOR_OCA,
)


class TestFiscalDocumentNFeCommon(TransactionCase):
    def setUp(self):
        super().setUp()

        self.nfe_same_state = self.env.ref("l10n_br_fiscal.demo_nfe_same_state")
        self.company = self.env.ref("l10n_br_base.empresa_simples_nacional")

        self.company.processador_edoc = PROCESSADOR_OCA
        self.company.partner_id.inscr_mun = "35172"
        self.company.partner_id.inscr_est = ""
        self.company.partner_id.state_id = self.env.ref("base.state_br_mg")
        self.company.partner_id.city_id = self.env.ref("l10n_br_base.city_3132404")
        self.company.icms_regulation_id = self.env.ref(
            "l10n_br_fiscal.tax_icms_regulation"
        ).id
        # self.company.city_taxation_code_id = self.env.ref(
        #     "l10n_br_fiscal.city_taxation_code_itajuba"
        # )
        self.company.document_type_id = self.env.ref("l10n_br_fiscal.document_55")
        self.nfe_same_state.company_id = self.company.id
        self.nfe_same_state.fiscal_operation_id = self.env.ref("l10n_br_fiscal.fo_venda").id

    def test_nfe_same_state_ibscbs_fiscal_operation(self):
        """Test Certified NFSe same state."""

        self.nfe_same_state._onchange_document_serie_id()
        self.nfe_same_state._onchange_fiscal_operation_id()

        for line in self.nfe_same_state.fiscal_line_ids:
            line.update({
                "icms_tax_id": self.env.ref("l10n_br_fiscal.tax_icms_12_st").id,
                "icmsst_tax_id": self.env.ref("l10n_br_fiscal.tax_icmsst_p30_50").id,
                "icmsfcpst_tax_id": self.env.ref("l10n_br_fiscal.tax_icmsfcp_st_2").id,
                "ipi_tax_id": self.env.ref("l10n_br_fiscal.tax_ipi_30").id,
                "pis_tax_id": self.env.ref("l10n_br_fiscal.tax_pis_1_65").id,
                "cofins_tax_id": self.env.ref("l10n_br_fiscal.tax_cofins_7_6").id,
                "ibsuf_tax_id": self.env.ref("l10n_br_account_nfe_IBSCBS.tax_ibsuf_000001").id,
                "ibsmun_tax_id": self.env.ref("l10n_br_account_nfe_IBSCBS.tax_ibsmun_000001").id,
                "cbs_tax_id": self.env.ref("l10n_br_account_nfe_IBSCBS.tax_cbs_000001").id,
            })
            line._onchange_product_id_fiscal()
            line._onchange_commercial_quantity()
            line._onchange_fiscal_operation_id()
            line._onchange_fiscal_operation_line_id()
            line._onchange_fiscal_taxes()

        for line in self.nfe_same_state.fiscal_line_ids:
            self.assertEqual(line.ibscbs_base, 320.0)
            self.assertEqual(line.ibsuf_aliquota, 0.1)
            self.assertEqual(line.ibsuf_value, 0.32)
            self.assertEqual(line.cbs_value, 2.88)
            self.assertEqual(line.ibsmun_value, 0.0)
            break
