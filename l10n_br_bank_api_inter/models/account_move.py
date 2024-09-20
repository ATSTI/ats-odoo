# Copyright 2021 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import tempfile
import logging
from base64 import b64decode, b64encode

from PyPDF2 import PdfFileMerger

from odoo import _, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):

    _inherit = "account.move"

    # pdf_boletos_id = fields.Many2one(
    #     comodel_name="ir.attachment", string="PDF Boletos", ondelete="cascade"
    # )

    # def _merge_pdf_boletos(self):
    #     # pdf_merger = PdfFileMerger()

    #     # temp_files = []
    #     for move_line in self.financial_move_line_ids:
    #         move_line.generate_pdf_boleto()

        #     if move_line.pdf_boleto_id:
        #         temp_pdf = tempfile.TemporaryFile()
        #         decode_data = b64decode(move_line.pdf_boleto_id.datas, validate=True)
        #         temp_pdf.write(decode_data)
        #         temp_pdf.seek(0)
        #         pdf_merger.append(temp_pdf)
        #         temp_files.append(temp_pdf)

        #         temp_merged = tempfile.TemporaryFile()
        #         pdf_merger.write(temp_merged)
        #         pdf_merger.close()

        #         temp_merged.seek(0)
        #         datas = b64encode(temp_merged.read())

        # self.pdf_boletos_id = self.env["ir.attachment"].create(
        #     {
        #         "name": ("Boleto %s" % self.display_name.replace("/", "-")),
        #         "res_model": self._name,
        #         "res_id": self.id,
        #         "datas": datas,
        #         "mimetype": "application/pdf",
        #         "type": "binary",
        #     }
        # )

        # for file in temp_files:
        #     file.close()

    def action_pdf_boleto(self):
        """
        Generates and lists all the attachment ids for an Boleto PDF of the
        invoice
        :return: actions.act_window
        """
        import pudb;pu.db
        for move in self:
            for move_line in move.financial_move_line_ids:
                if not move_line.codigo_solicitacao:
                    # gerar boleto
                    move.payment_order_id.open2generated()
                    sleep(5)
                    break
        boleto_gerado = False
        for move_line in self.financial_move_line_ids:            
            if move_line.codigo_solicitacao and not move_line.pdf_boleto_id:
                try:
                    move_line.generate_pdf_boleto()
                    boleto_gerado = True
                except Exception as e:
                    _logger.error("Erro impressão PDF, tente novamente. Erro: \n {}".format(e))
            else:
                boleto_gerado = True
            # if not boleto_gerado:
                # raise UserError("Boleto não gerado. Verifique no menu Clientes/Debit Orders.")
            # if not self.pdf_boletos_id:
                # self._merge_pdf_boletos()
            # boleto_id = move_line.pdf_boleto_id
            # base_url = self.env["ir.config_parameter"].get_param("web.base.url")
            # download_url = "/web/content/%s/%s?download=True" % (
            #     str(boleto_id.id),
            #     boleto_id.name,
            # )

            # return {
            #     "type": "ir.actions.act_url",
            #     "url": str(base_url) + str(download_url),
            #     "target": "new",
            # }
        # try:
        #     if not self.pdf_boletos_id:
        #         self._merge_pdf_boletos()

        #     boleto_id = self.pdf_boletos_id
        #     base_url = self.env["ir.config_parameter"].get_param("web.base.url")
        #     download_url = "/web/content/%s/%s?download=True" % (
        #         str(boleto_id.id),
        #         boleto_id.name,
        #     )

        #     return {
        #         "type": "ir.actions.act_url",
        #         "url": str(base_url) + str(download_url),
        #         "target": "new",
        #     }
        # except Exception as error:
        #     raise UserError(error)

    # def action_invoice_cancel(self):
    #     try:
    #         for financial_move_line in self.financial_move_line_ids:
    #             financial_move_line.drop_bank_slip()
    #             if financial_move_line.bank_inter_state == "baixado":
    #                 return self.button_cancel()
    #             else:
    #                 raise UserError(
    #                     _(
    #                         "All Account Move Line related to Invoice must haver their "
    #                         "status set to 'write off' to be able to cancel."
    #                     )
    #                 )
    #     except Exception as error:
    #         raise UserError(_(error))

    # def _post(self, soft=True):
    #     res = super()._post(soft=soft)
    #     if not self.pdf_boletos_id:
    #         self.action_pdf_boleto()
    #     return res

    def load_cnab_info(self):
        import pudb;pu.db
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
                # '{"seuNumero":"PAY0161","nossoNumero":"01345006506","codigoBarras":"07792974600000007800001112063827901345006506","linhaDigitavel":"0779000116     account_move.py:61 (0 hit
                # 1206382790613450065068297460000000780"}'
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
                        #     pay.open2generated()
        return res
