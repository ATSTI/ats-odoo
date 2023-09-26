# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ContractContract(models.Model):
    _inherit = "contract.contract"

    def _recurring_create_invoice(self, date_ref=False):
        moves = super()._recurring_create_invoice(date_ref)
        for move in moves:
            # Validar a Fatura
            move.action_post()
            # Envia a NFSe
            if move.document_type_id:
                move.fiscal_document_id.action_document_send()
            # Enviar o Boleto (IUGU nao precisa, ja e feito por la)
        return moves
