# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models


class AccountPaymentOrder(models.Model):
    _inherit = "account.payment.order"

    def _generate_bank_inter_boleto_data(self):
        data = super()._generate_bank_inter_boleto_data()

        for line in self.payment_line_ids:
            if line.partner_id.desconto_boleto_inter:
                # vencimento = line.ml_maturity_date.strftime("%Y-%m-%d")
                desconto = {
                    "taxa": line.partner_id.desconto_boleto_inter / 100,
                    "codigo": "PERCENTUALDATAINFORMADA",
                    "quantidadeDias": 0,
                }
                for item in data:
                    if item._identifier == line.document_number:
                        item.discount1 = desconto
        return data
