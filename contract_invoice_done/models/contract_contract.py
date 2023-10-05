# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, _


class ContractContract(models.Model):
    _inherit = "contract.contract"

    def _recurring_create_invoice(self, date_ref=False):
        moves = super()._recurring_create_invoice(date_ref)
        for move in moves:
            errors = []
            try:
                if not move.fiscal_operation_id and self.fiscal_operation_id:
                    move.fiscal_operation_id = self.fiscal_operation_id.id
                    move.fiscal_document_id._onchange_document_serie_id()
                    move.fiscal_document_id._onchange_company_id()
                    move._onchange_invoice_line_ids()
                # valida se boleto iugu
                if move.payment_journal_id.receive_by_iugu:
                    errors = move.validate_data_iugu()
                # Validar a Fatura
                move.action_post()
                # Envia a NFSe
                if move.document_type_id:
                    errors.append("Erro na transmissão do documento fiscal")
                    move.fiscal_document_id.action_document_send()
                # Enviar o Boleto (IUGU nao precisa, ja e feito por la)
                # errors.append("Erro na geracao do boleto")
                # move.generate_payment_transactions()
                if move.payment_journal_id.receive_by_iugu:
                    msg = move.send_information_to_iugu()
                    errors.append(msg)
            except:
                if len(errors) and len(errors[0]) > 0:
                    self.message_post(
                        body=_(
                            "<a href='#' data-oe-model='%s' data-oe-id='%s'>Fatura criada</a> Erro '%s'"
                        ) % (move._name, move.id, errors[0])
                    )
                    move.message_post(
                        body=_(
                            "<a href='#' data-oe-model='%s' data-oe-id='%s'>Gerado pelo contrato</a> Erro '%s'"
                        ) % (self._name, self.id, errors[0])
                    )
                errors = []
            if len(errors) and len(errors[0]) > 0:
                self.message_post(
                    body=_(
                        "<a href='#' data-oe-model='%s' data-oe-id='%s'>Fatura criada</a> Erro '%s'"
                    ) % (move._name, move.id, errors[0])
                )
                move.message_post(
                    body=_(
                            "<a href='#' data-oe-model='%s' data-oe-id='%s'>Gerado pelo contrato</a> Erro '%s'"
                    ) % (self._name, self.id, errors[0])
                )
        return moves
