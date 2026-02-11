from odoo import models, api
import logging
import re

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.model
    def create_from_ui(self, orders, draft=False):

        res = super().create_from_ui(orders, draft)

        for payload, result in zip(orders, res):
            cpf_raw = payload.get("data", {}).get("extra_note")

            if not cpf_raw:
                continue

            cpf = re.sub(r"\D", "", cpf_raw)

            if not cpf:
                continue

            order = self.browse(result["id"])

            if "cnpj_cpf" in order._fields:
                order.sudo().write({"cnpj_cpf": cpf})
                _logger.warning("CPF salvo no pedido POS: %s", cpf)
            else:
                _logger.warning("Campo cnpj_cpf não existe no pos.order")

        return res

    
