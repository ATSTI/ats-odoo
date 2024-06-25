# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FiscalDocumentTransp(models.Model):
    _inherit = "l10n_br_fiscal.document"

    def _prepare_nfce_danfe_line_values(self):
        lines_list = []
        lines = self.fiscal_line_ids.filtered(lambda line: line.product_id)
        for index, line in enumerate(lines):
            product_id = line.product_id
            lines_list.append(
                {
                    "product_index": index + 1,
                    "product_default_code": product_id.default_code,
                    "product_name": product_id.name,
                    "product_quantity": line.quantity,
                    "product_uom": product_id.uom_name,
                    "product_unit_value": line.price_unit,
                    "product_unit_total": line.quantity * line.price_unit,
                }
            )
        return lines_list

    def _prepare_nfce_danfe_values(self):
        return {
            "company_ie": self.company_id.inscr_est,
            "company_cnpj": self.company_id.cnpj_cpf,
            "company_legal_name": self.company_id.legal_name,
            "company_name": self.company_id.name,
            "company_street": self.company_id.street,
            "company_number": self.company_id.street_number,
            "company_district": self.company_id.district,
            "company_city": self.company_id.city_id.display_name,
            "company_state": self.company_id.state_id.name,
            "partner_cpf": self.move_ids.cpf_consumidor or '',
            "lines": self._prepare_nfce_danfe_line_values(),
            "total_product_quantity": len(
                self.fiscal_line_ids.filtered(lambda line: line.product_id)
            ),
            "amount_total": self.amount_total,
            "amount_discount_value": self.amount_discount_value,
            "amount_freight_value": self.amount_freight_value,
            "payments": self._prepare_nfce_danfe_payment_values(),
            "amount_change": self.nfe40_vTroco,
            "nfce_url": self.get_nfce_qrcode_url(),
            "document_key": self.document_key,
            "document_number": self.document_number,
            "document_serie": self.document_serie,
            "document_date": self.document_date.astimezone().strftime(
                "%d/%m/%y %H:%M:%S"
            ),
            "authorization_protocol": self.authorization_protocol,
            "document_qrcode": self.get_nfce_qrcode(),
            "system_env": self.nfe40_tpAmb,
            "unformatted_amount_freight_value": self.amount_freight_value,
            "unformatted_amount_discount_value": self.amount_discount_value,
            "contingency": self.nfe_transmission != "1",
            "homologation_environment": self.nfe_environment == "2",
        }