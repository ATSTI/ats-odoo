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

            _logger.warning("CPF RAW recebido do POS: %s", cpf_raw)

            if not cpf_raw:
                continue

            cpf = re.sub(r"\D", "", cpf_raw)

            order = self.browse(result["id"])

            _logger.warning(
                "Aplicando CPF no pedido %s -> %s",
                order.pos_reference,
                cpf,
            )

            # ✅ campo usado pelo XML NFC-e
            if hasattr(order, "customer_tax_id"):
                order.customer_tax_id = cpf
                _logger.warning("customer_tax_id gravado")

            # ✅ salva no partner também (garantia DANFE)
            if order.partner_id:
                if hasattr(order.partner_id, "cnpj_cpf"):
                    order.partner_id.cnpj_cpf = cpf
                    _logger.warning("partner.cnpj_cpf gravado")
                else:
                    order.partner_id.vat = cpf
                    _logger.warning("partner.vat gravado")

            # opcional — manter seu campo custom
            if hasattr(order, "extra_note"):
                order.extra_note = cpf

        _logger.warning("=== CPF HOOK FINALIZADO ===")

        return res
