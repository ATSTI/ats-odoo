# Copyright 2021 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import tempfile
from base64 import b64decode, b64encode

from PyPDF2 import PdfFileMerger

from odoo import _, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):

    _inherit = "account.move"

    pdf_boletos_id = fields.Many2one(
        comodel_name="ir.attachment", string="PDF Boletos", ondelete="cascade"
    )

    def _merge_pdf_boletos(self):
        pdf_merger = PdfFileMerger()

        temp_files = []
        for move_line in self.financial_move_line_ids:
            move_line.generate_pdf_boleto()

            if move_line.pdf_boleto_id:
                temp_pdf = tempfile.TemporaryFile()
                decode_data = b64decode(move_line.pdf_boleto_id.datas, validate=True)
                temp_pdf.write(decode_data)
                temp_pdf.seek(0)
                pdf_merger.append(temp_pdf)
                temp_files.append(temp_pdf)

        temp_merged = tempfile.TemporaryFile()
        pdf_merger.write(temp_merged)
        pdf_merger.close()

        temp_merged.seek(0)
        datas = b64encode(temp_merged.read())

        self.pdf_boletos_id = self.env["ir.attachment"].create(
            {
                "name": ("Boleto %s" % self.display_name.replace("/", "-")),
                "datas": datas,
                "type": "binary",
                "res_id": self.id,
            }
        )

        for file in temp_files:
            file.close()

    def action_pdf_boleto(self):
        """
        Generates and lists all the attachment ids for an Boleto PDF of the
        invoice
        :return: actions.act_window
        """
        try:
            if not self.pdf_boletos_id:
                self._merge_pdf_boletos()

            boleto_id = self.pdf_boletos_id
            base_url = self.env["ir.config_parameter"].get_param("web.base.url")
            download_url = "/web/content/%s/%s?download=True" % (
                str(boleto_id.id),
                boleto_id.name,
            )

            return {
                "type": "ir.actions.act_url",
                "url": str(base_url) + str(download_url),
                "target": "new",
            }
        except Exception as error:
            raise UserError(error)

    def action_invoice_cancel(self):
        try:
            for financial_move_line in self.financial_move_line_ids:
                financial_move_line.drop_bank_slip()
                if financial_move_line.bank_inter_state == "baixado":
                    return self.button_cancel()
                else:
                    raise UserError(
                        _(
                            "All Account Move Line related to Invoice must haver their "
                            "status set to 'write off' to be able to cancel."
                        )
                    )
        except Exception as error:
            raise UserError(_(error))

    def load_cnab_info(self):
        # Se não possui Modo de Pagto não há nada a ser feito
        if not self.payment_mode_id:
            return
        # Se o Modo de Pagto é de saída (pgto fornecedor) não há nada a ser feito.
        if self.payment_mode_id.payment_type == "outbound":
            return
        # Se não gera Ordem de Pagto não há nada a ser feito
        if not self.payment_mode_id.payment_order_ok:
            return
        if (
            self.partner_bank_id.bank_id
            != self.env.ref("l10n_br_base.res_bank_077")
            and self.payment_mode_id.payment_method_id.code != "electronic"
            ):
            return super().generate_payment_file()
        else:
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
                pay_order_id = filtered_invoice_ids.create_account_payment_line()
                # z = filtered_invoice_ids.payment_order_id
                # Confirmar payment
                pay = self.env['account.payment.order'].browse([pay_order_id['res_id']])
                if pay:
                    pay.draft2open()
                    pay.open2generated()
