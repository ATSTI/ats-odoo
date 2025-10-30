# -*- coding: utf-8 -*-

from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()

        # Define desconto global
        invoice_vals['discount_type'] = 'amount'
        invoice_vals['discount_rate'] = self.amount_discount_value or 0.0
        if invoice_vals['document_type_id'] == 40:  # Nota Fiscal de Serviço
            lines_with_fiscal_op_line = self.order_line.filtered(
                lambda ln: ln.fiscal_operation_line_id
            )
            service_lines = lines_with_fiscal_op_line.filtered(
                lambda l: l.fiscal_operation_line_id.get_document_type(l.company_id).id == 40
            )

            if service_lines:
                total_services = sum(line.price_unit * line.quantity for line in service_lines)
                total_discount = self.amount_discount_value or 0.0
                proportion = total_services / self.amount_price_gross if self.amount_price_gross else self.amount_untaxed
                invoice_vals['discount_rate'] = self.currency_id.round(total_discount * proportion)
        if invoice_vals['document_type_id'] == 31:
            lines_with_fiscal_op_line = self.order_line.filtered(
                lambda ln: ln.fiscal_operation_line_id
            )
            product_lines = lines_with_fiscal_op_line.filtered(
                lambda l: l.fiscal_operation_line_id.get_document_type(l.company_id).id == 31
            )

            if product_lines:
                total_products = sum(line.price_unit * line.quantity for line in product_lines)
                total_discount = self.amount_discount_value or 0.0
                proportion = total_products / self.amount_price_gross if self.amount_price_gross else self.amount_untaxed
                invoice_vals['discount_rate'] = self.currency_id.round(total_discount * proportion)
        return invoice_vals