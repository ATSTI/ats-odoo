from odoo import models, api
import logging
import re

_logger = logging.getLogger(__name__)

class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.model
    def create_from_ui(self, orders, draft=False):
        _logger.warning("=== CPF HOOK create_from_ui ENTROU ===")

        # Chama o método original para criar os pedidos
        res = super().create_from_ui(orders, draft)
        import pudb;pudb.set_trace()
        for payload, result in zip(orders, res):
            data = payload.get("data", {})
            cpf_raw = data.get("extra_note")  # do POS JS

            if not cpf_raw:
                continue

            cpf = re.sub(r"\D", "", cpf_raw)  

            order = self.browse(result["id"])
            _logger.warning("CPF aplicado no pedido POS: %s", cpf)

            if hasattr(order, "customer_tax_id"):
                order.customer_tax_id = cpf
            if hasattr(order, "cnpj_cpf"):
                order.cnpj_cpf = cpf
            if hasattr(order, "extra_note"):
                order.extra_note = cpf

            if order.invoice_id:
                invoice = order.invoice_id
                if hasattr(invoice, "cpf_consumidor"):
                    invoice.cpf_consumidor = cpf
                    _logger.warning("CPF aplicado na fatura: %s", cpf)

        return res
