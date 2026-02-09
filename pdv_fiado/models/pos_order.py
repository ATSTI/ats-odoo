from odoo import models, api
import logging
import re

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.model
    def create_from_ui(self, orders, draft=False):
        _logger.warning("=== CPF HOOK create_from_ui ENTROU ===")

        res = super().create_from_ui(orders, draft)

        for payload, result in zip(orders, res):
            data = payload.get("data", {})
            cpf_raw = data.get("extra_note")

            if not cpf_raw:
                continue

            cpf = re.sub(r"\D", "", cpf_raw)

            order = self.browse(result["id"])

            _logger.warning("CPF aplicado na NFC-e: %s", cpf)

            # ✅ grava só no pedido fiscal
            if hasattr(order, "customer_tax_id"):
                order.customer_tax_id = cpf

            if hasattr(order, "cnpj_cpf"):
                order.cnpj_cpf = cpf

            if hasattr(order, "extra_note"):
                order.extra_note = cpf

     return res
