# Copyright 2021 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import time
import logging
from base64 import b64decode, b64encode

from PyPDF2 import PdfFileMerger

from odoo import _, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"

    def action_pdf_boleto(self):
        """
        Generates and lists all the attachment ids for an Boleto PDF of the
        invoice
        :return: actions.act_window
        """
        for move in self:
            for move_line in move.financial_move_line_ids:
                if not move_line.codigo_solicitacao:
                    # gerar boleto
                    move.payment_order_id.open2generated()
                    time.sleep(5)
                    break
        for move_line in self.financial_move_line_ids:            
            if move_line.codigo_solicitacao and not move_line.pdf_boleto_id:
                try:
                    move_line.generate_pdf_boleto()
                except Exception as e:
                    _logger.error("Erro impressão PDF, tente novamente. Erro: \n {}".format(e))

    def load_cnab_info(self):
        res = super().load_cnab_info()
        if (
            self.partner_bank_id.bank_id
            == self.env.ref("l10n_br_base.res_bank_077")
            and self.payment_mode_id.payment_method_id.code == "electronic"
            ):
                # TODO - apesar do campo financial_move_line_ids ser do tipo
                #  compute esta sendo preciso chamar o metodo porque as vezes
                #  ocorre da linha vir vazia o que impede de entrar no FOR
                #  abaixo causando o não preenchimento de dados usados no Boleto,
                #  isso deve ser melhor investigado
                self._compute_financial()
                for index, interval in enumerate(self.financial_move_line_ids):
                    inv_number = self.get_invoice_fiscal_number().split("/")[-1]
                    numero_documento = inv_number + "/" + str(index + 1).zfill(2)

                    #sequence = self.payment_mode_id.own_number_sequence_id.next_by_id()

                    # vem do Inter
                    # interval.own_number = (
                    #     sequence if interval.payment_mode_id.generate_own_number else "0"
                    # )
                    interval.document_number = numero_documento
                    interval.company_title_identification = hex(interval.id).upper()
                    instructions = ""
                    if self.eval_payment_mode_instructions:
                        instructions = self.eval_payment_mode_instructions + "\n"
                    if self.instructions:
                        instructions += self.instructions + "\n"
                    interval.instructions = instructions
                    # Codigo de Instrução do Movimento pode variar,
                    # mesmo no CNAB 240
                    # interval.mov_instruction_code_id = (
                    #     self.payment_mode_id.cnab_sending_code_id.id
                    # )
                filtered_invoice_ids = self.filtered(
                    lambda s: (
                        s.payment_mode_id and s.payment_mode_id.auto_create_payment_order
                    )
                )
                if filtered_invoice_ids:
                    # Criação das Linha na Ordem de Pagamento
                    applicable_lines = False
                    for move in self:
                        if move.state != "posted":
                            raise UserError(_("The invoice %s is not in Posted state") % move.name)
                        applicable_lines = move.line_ids.filtered(
                            lambda x: (
                                not x.reconciled
                                and x.payment_mode_id.payment_order_ok
                                and x.account_id.internal_type in ("receivable", "payable")
                                and not any(
                                    p_state in ("draft", "open", "generated")
                                    for p_state in x.payment_line_ids.mapped("state")
                                )
                            )
                        )
                    if applicable_lines:
                        pay_order_id = filtered_invoice_ids.create_account_payment_line()
                        pay = self.env['account.payment.order'].browse([pay_order_id['res_id']])
                        if not self.payment_order_id:
                            # nao sei pq este campo nao e gravado
                            self.payment_order_id = pay_order_id['res_id']
                        pay.draft2open()
        return res
