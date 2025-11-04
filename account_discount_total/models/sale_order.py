# -*- coding: utf-8 -*-

from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _normalize_line_sequence(self):
        """Garante que a sequência das linhas reflita a ordem visual real"""
        for order in self:
            for index, line in enumerate(order.order_line.sorted(key=lambda l: l.id), start=1):
                if line.sequence != index:
                    line.sequence = index

    def _prepare_invoice(self):
        self._normalize_line_sequence()
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        # Define desconto global
        invoice_vals['discount_type'] = 'amount'
        if self.fiscal_operation_id:
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
        else:
            invoice_vals['discount_rate'] = self.amount_discount_value or 0.0
        return invoice_vals
    
    def _create_invoices(self, grouped=False, final=False, date=None):
        res = super(SaleOrder, self)._create_invoices(grouped=False, final=False, date=None)
        service_line_t = res.invoice_line_ids.filtered(
            lambda l: l.product_id.detailed_type == "service"
        )
        if service_line_t:
            sequence_line = service_line_t.sequence - 1
            for move in res:
                if any(line.product_id.detailed_type == "service" for line in move.invoice_line_ids):
                    for lines in move.invoice_line_ids:
                        if lines.sequence < sequence_line and lines.display_type == "line_section":
                            lines.unlink()
                else:
                    for lines in move.invoice_line_ids:
                        if lines.sequence == sequence_line:
                            lines.unlink()
        return res

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_invoice_line(self, **optional_values):
        if "sequence" in optional_values:
            optional_values['sequence'] = self.sequence
        vals = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)

        return vals