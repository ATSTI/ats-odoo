# from odoo import models, api
# import logging
# import re

# _logger = logging.getLogger(__name__)


# class PosOrder(models.Model):
#     _inherit = "pos.order"


#     def _setup_anonymous_consumer(self):
#         if self._has_anonymous_consumer():
#             import pudb;pudb.set_trace()
#             if len(self.cnpj_cpf) == 14:
#                 self.partner_id.write(
#                     {
#                         "company_type": "company",
#                         "ind_ie_dest": "9",
#                     }
#                 )
#                 self.partner_id.nfe40_CPF = ""
#             else:
#                 self.partner_id.nfe40_CNPJ = ""
#             self.partner_id.write({"cnpj_cpf": self.cnpj_cpf})
#             self.account_move.fiscal_document_id.nfe40_dest.nfe40_xNome = ""

#     # @api.model
#     # def create_from_ui(self, orders, draft=False):

#     #     res = super().create_from_ui(orders, draft)

#     #     for payload, result in zip(orders, res):
#     #         cpf_raw = payload.get("data", {}).get("extra_note")

#     #         if not cpf_raw:
#     #             continue

#     #         cpf = re.sub(r"\D", "", cpf_raw)

#     #         if not cpf:
#     #             continue

#     #         order = self.browse(result["id"])

#     #         if "cnpj_cpf" in order._fields:
#     #             order.sudo().write({"cnpj_cpf": cpf})
#     #             _logger.warning("CPF salvo no pedido POS: %s", cpf)
#     #         else:
#     #             _logger.warning("Campo cnpj_cpf não existe no pos.order")

#     #     return res

    
