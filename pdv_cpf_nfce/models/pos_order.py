from odoo import models

from odoo.addons.l10n_br_fiscal.constants.fiscal import MODELO_FISCAL_NFCE


class PosOrder(models.Model):
    _inherit = "pos.order"

    def _setup_anonymous_consumer(self):
        # Garante que o parceiro anônimo compartilhado não carregue
        # resíduo de uma venda anterior que não foi limpa corretamente.
        if self.partner_id.is_anonymous_consumer and not self.cnpj_cpf:
            if self.partner_id.cnpj_cpf:
                self.partner_id.write(
                    {"company_type": "person", "cnpj_cpf": False}
                )
                self.partner_id.nfe40_CPF = ""
                self.partner_id.nfe40_CNPJ = ""

        return super()._setup_anonymous_consumer()