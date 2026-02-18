# Copyright (C) KMEE 2023
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import logging

from odoo import api, fields, models

from odoo.addons.l10n_br_fiscal.constants.fiscal import MODELO_FISCAL_NFCE

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = "pos.order"

    def _generate_pos_order_invoice(self):
        invoice = super()._generate_pos_order_invoice()
        return invoice

    def _create_invoice(self, move_vals):
        res = super()._create_invoice(move_vals)
        for line in self.lines:
            for inv_line in res.line_ids:
                if inv_line.product_id == line.product_id and inv_line.quantity == line.qty:
                    if inv_line.fiscal_quantity != line.qty:
                        inv_line.write({"fiscal_quantity": line.qty})
        return res

    def _prepare_invoice_vals(self):
        vals = super()._prepare_invoice_vals()

        pos_config_id = self.session_id.config_id
        nfce_vals = self._prepare_nfce_vals(pos_config_id)
        vals.update(nfce_vals)

        return vals

    def _prepare_nfce_vals(self, pos_config_id):
        if not self.payment_ids:
            return dict()
        payment_mode_id = self.env['account.payment.mode'].search([
            ('fixed_journal_id', '=', self.payment_ids[0].payment_method_id.journal_id.id)
        ])  # Default payment mode

        return {
            "document_type_id": 31,  # NFC-e
            "fiscal_operation_id": 1,  # Venda de Mercadoria
            "ind_pres": "1",
            "document_serie_id": 1,  # Série padrão NFC-e
            "partner_id": self.partner_id.id,
            "payment_mode_id": payment_mode_id[0].id,
            "nfe40_vTroco": 0.0,
        }

    def _prepare_invoice_line(self, order_line):
        vals = super()._prepare_invoice_line(order_line)

        vals.update(order_line._prepare_nfce_tax_dict())

        return vals


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    def _prepare_nfce_tax_dict(self):
        fiscal_operation_id = self.env['l10n_br_fiscal.operation'].browse([1])  # Venda de Mercadoria

        fiscal_operation_line_id = fiscal_operation_id.line_definition(
                        company=self.order_id.company_id,
                        partner=self.order_id.partner_id,
                        product=self.product_id,
                    )

        mapping_result = fiscal_operation_line_id.map_fiscal_taxes(
                    company=self.order_id.company_id,
                    partner=self.order_id.partner_id,
                    product=self.product_id,
                    ncm=self.product_id.ncm_id,
                    nbm=self.product_id.nbm_id,
                    nbs=self.product_id.nbs_id,
                    cest=self.product_id.cest_id,
                    city_taxation_code=self.product_id.city_taxation_code_ids,
                    national_taxation_code=self.env['l10n_br_fiscal.national.taxation.code'],
                    service_type=self.product_id.service_type_id,
                    ind_final=self.order_id.partner_id.ind_final,
                )

        cfop_id = mapping_result["cfop"]
        ipi_guideline_id = mapping_result["ipi_guideline"]
        icms_tax_benefit_id = mapping_result["icms_tax_benefit_id"]

        taxes = self.env["l10n_br_fiscal.tax"]
        for tax in mapping_result["taxes"].values():
            taxes |= tax
        fiscal_tax_ids = taxes

        # Create base tax_dict
        tax_dict = {
            "fiscal_operation_id": fiscal_operation_id.id,
            "fiscal_operation_line_id": fiscal_operation_line_id.id,
            "cfop_id": cfop_id.id,
            "fiscal_genre_id": self.product_id.fiscal_genre_id.id,
            "uom_id": self.product_id.uom_id.id,
            "uot_id": self.product_id.uom_id.id,
            "ncm_id": self.product_id.ncm_id.id,
        }
        # "discount_value": (self.discount * self.amount_total) / 100,
        # "uot_id": mapping_result.uot_id.id,

        #         # Update tax dict for each tax domain
        #         tax_dict.update(self._prepare_nfce_icms_dict(fiscal_map_id))
        #         tax_dict.update(self._prepare_nfce_ipi_dict(fiscal_map_id))
        #         tax_dict.update(self._prepare_nfce_cofins_dict(fiscal_map_id))
        #         tax_dict.update(self._prepare_pis_icms_dict(fiscal_map_id))
        #         tax_dict.update(self._prepare_pis_icms_dict(fiscal_map_id))
        #         # Update tax dict with fiscal_tax_ids data
        #         tax_dict.update(self._prepare_nfce_fiscal_tax_ids(fiscal_map_id))

        return tax_dict
