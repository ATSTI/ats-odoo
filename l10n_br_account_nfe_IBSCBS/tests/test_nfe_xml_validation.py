import logging

from odoo.tests.common import TransactionCase
from odoo.tools import float_compare

from odoo.addons.l10n_br_fiscal.constants.fiscal import SITUACAO_EDOC_A_ENVIAR

_logger = logging.getLogger(__name__)


class TestXMLValidation(TransactionCase):
    def test_xml_nfe_taxes(self):
        """This method tests multiple tax fields for NFe lines and NFe totals.
        warning: failures in this method could indicate errors in fiscal or account
        """
        move_model = self.env["account.move"]
        move_line_model = self.env["account.move.line"]
        akretion_partner = self.env.ref("l10n_br_base.res_partner_cliente7_rs")
        company_id = self.env.ref("l10n_br_base.empresa_lucro_presumido")
        self.env.user.company_ids += company_id
        self.env.user.company_id = company_id

        invoice_journal = self.env["account.journal"].create(
            {
                "company_id": company_id.id,
                "name": "Invoice Journal - (test)",
                "code": "INVTEST",
                "type": "sale",
            }
        )

        move = move_model.create(
            {
                "partner_id": akretion_partner.id,
                "ind_final": "0",
                "move_type": "out_invoice",
                'invoice_date': '2017-01-01',
                'date': '2017-01-01',
                'partner_id': self.partner_id.id,
                'currency_id': self.currency_data['currency'].id,
                "document_type_id": self.env.ref("l10n_br_fiscal.document_55").id,
                "document_serie_id": self.env.ref("l10n_br_fiscal.document_55_serie_1").id,
                "fiscal_operation_id": self.env.ref("l10n_br_fiscal.fo_venda").id,
            }
        ).with_context(default_move_type='out_invoice')

                # "journal_id": invoice_journal.id,

        # invoice = self.env['account.move'].create({
        #     'move_type': 'out_invoice',
        #     'invoice_date': '2017-01-01',
        #     'date': '2017-01-01',
        #     'partner_id': self.partner_a.id,
        #     'currency_id': self.currency_data['currency'].id,
        #     'fiscal_position_id': fiscal_position.id,
        #     'invoice_line_ids': [
        #         Command.create({
        #             'name': 'test line',
        #             'product_id': product.id,
        #         }),
        #     ],
        # })


        # "journal_id": self.env.ref("l10n_br_account.account_journal_nfe_saida").id,
        move._onchange_fiscal_operation_id()
        move._onchange_document_type_id()
        move._onchange_document_serie_id()

        invoice_line_account_id = self.env["account.account"].create(
            {
                "company_id": company_id.id,
                "user_type_id": self.env.ref("account.data_account_type_revenue").id,
                "code": "705070",
                "name": "Product revenue account (test)",
            }
        )

        # Line 1
        line = move_line_model.create(
            {
                "move_id": move.id,
                "fiscal_operation_id": move.fiscal_operation_id.id,
                "product_id": self.env.ref("product.product_product_4c").id,
                "price_unit": 116.41,
                "fiscal_price": 116.41,
                "quantity": 22,
                "fiscal_quantity": 22,
                "account_id": invoice_line_account_id.id,
            }
        )
        line._onchange_product_id_fiscal()
        line._onchange_fiscal_operation_line_id()

        # Force taxes
        line.update(
            {
                "icms_tax_id": self.env.ref("l10n_br_fiscal.tax_icms_12_st").id,
                "icmsst_tax_id": self.env.ref("l10n_br_fiscal.tax_icmsst_p30_50").id,
                "icmsfcpst_tax_id": self.env.ref("l10n_br_fiscal.tax_icmsfcp_st_2").id,
                "ipi_tax_id": self.env.ref("l10n_br_fiscal.tax_ipi_30").id,
                "pis_tax_id": self.env.ref("l10n_br_fiscal.tax_pis_1_65").id,
                "cofins_tax_id": self.env.ref("l10n_br_fiscal.tax_cofins_7_6").id,
                "ibscbs_tax_id": self.env.ref("l10n_br_account_nfe_IBSCBS.tax_ibscbs_000001").id,
                "ibscbs_cst_id": self.env.ref("l10n_br_account_nfe_IBSCBS.cst_ibscbs_000001").id,
                "ibsuf_tax_id": self.env.ref("l10n_br_account_nfe_IBSCBS.tax_ibsuf_000001").id,
                "ibsmun_tax_id": self.env.ref("l10n_br_account_nfe_IBSCBS.tax_ibsmun_000001").id,
                "cbs_tax_id": self.env.ref("l10n_br_account_nfe_IBSCBS.tax_ibs_000001").id,
            }
        )
        line._onchange_fiscal_taxes()
        x = line.fiscal_operation_line_id.name
        import pudb;pu.db
        # line._prepare_tax_ibscbs()
        # line.account_line_ids._prepare_tax_ibscbs()

        # Line 2 - using two lines to test the XML totals
        line2 = move_line_model.create(
            {
                "move_id": move.id,
                "fiscal_operation_id": move.fiscal_operation_id.id,
                "product_id": self.env.ref("product.product_product_4c").id,
                "price_unit": 116.41,
                "fiscal_price": 116.41,
                "quantity": 22,
                "fiscal_quantity": 22,
                "account_id": invoice_line_account_id.id,
            }
        )
        line2._onchange_product_id_fiscal()
        line2._onchange_fiscal_operation_line_id()
        # line.account_line_ids._prepare_tax_ibscbs()

        # Force taxes
        line2.update(
            {
                "icms_tax_id": self.env.ref("l10n_br_fiscal.tax_icms_12_st").id,
                "icmsst_tax_id": self.env.ref("l10n_br_fiscal.tax_icmsst_p30_50").id,
                "icmsfcpst_tax_id": self.env.ref("l10n_br_fiscal.tax_icmsfcp_st_2").id,
                "ipi_tax_id": self.env.ref("l10n_br_fiscal.tax_ipi_30").id,
                "pis_tax_id": self.env.ref("l10n_br_fiscal.tax_pis_1_65").id,
                "cofins_tax_id": self.env.ref("l10n_br_fiscal.tax_cofins_7_6").id,
                "ibscbs_tax_id": self.env.ref("l10n_br_account_nfe_IBSCBS.tax_ibscbs_000001").id,
                "ibscbs_cst_id": self.env.ref("l10n_br_account_nfe_IBSCBS.cst_ibscbs_000001").id,
                "ibsuf_tax_id": self.env.ref("l10n_br_account_nfe_IBSCBS.tax_ibsuf_000001").id,
                "ibsmun_tax_id": self.env.ref("l10n_br_account_nfe_IBSCBS.tax_ibsmun_000001").id,
                "cbs_tax_id": self.env.ref("l10n_br_account_nfe_IBSCBS.tax_ibs_000001").id,
            }
        )
        line2._onchange_fiscal_taxes()

        move.post()

        # This section probably indicates an error in eiter
        #   l10n_br_account or l10n_br_fiscal
        self.assertEqual(line.icms_value, 307.32)
        self.assertEqual(line.icmsst_value, 1190.88)
        self.assertEqual(line.icmsfcpst_value, 99.88)
        self.assertEqual(float_compare(line.ipi_value, 768.31, precision_digits=2), 0)
        self.assertEqual(line.pis_value, 42.26)
        self.assertEqual(
            float_compare(line.cofins_value, 194.64, precision_digits=2), 0
        )
        self.assertEqual(line.nfe40_vIBSMun, 0.00)
        # self.assertEqual(line.nfe40_vIBSUF, 2.56)
        self.assertEqual(line.nfe40_vCBS, 23.05)

        # This section actually tests NFe fields and values
        self.assertEqual(move.nfe40_vICMS, 614.64)
        self.assertEqual(move.nfe40_vST, 2381.76)
        self.assertEqual(move.nfe40_vFCPST, 199.76)
        self.assertEqual(
            float_compare(move.nfe40_vIPI, 1536.62, precision_digits=2), 0
        )
        self.assertEqual(move.nfe40_vPIS, 84.52)
        self.assertEqual(
            float_compare(move.nfe40_vCOFINS, 389.28, precision_digits=2), 0
        )
        
