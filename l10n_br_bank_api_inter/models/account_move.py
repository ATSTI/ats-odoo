# Copyright 2021 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import tempfile
from base64 import b64decode, b64encode
from PyPDF2 import PdfFileMerger

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountMove(models.Model):

    _inherit = 'account.move'


    def _merge_pdf_boletos(self):
        pdf_merger = PdfFileMerger()

        temp_files = []
        for move_line in self.financial_move_line_ids:
            move_line.generate_pdf_boleto()

            if move_line.pdf_boleto_id:
                temp_pdf = tempfile.TemporaryFile()
                bytes = b64decode(move_line.pdf_boleto_id.datas, validate=True)
                temp_pdf.write(bytes)
                temp_pdf.seek(0)
                pdf_merger.append(temp_pdf)
                temp_files.append(temp_pdf)

        temp_merged = tempfile.TemporaryFile()
        pdf_merger.write(temp_merged)
        pdf_merger.close()

        temp_merged.seek(0)
        datas = b64encode(temp_merged.read())

        self.file_boleto_pdf_id = self.env['ir.attachment'].create(
            {
                'name': (
                    "Boleto %s" % self.display_name.replace('/', '-')),
                'datas': datas,
                'datas_fname': ("boleto_%s.pdf" %
                                self.display_name.replace('/', '-')),
                'type': 'binary'
            }
        )

        for file in temp_files:
            file.close()

    def gera_boleto_pdf(self):
        """
        Generates and lists all the attachment ids for an Boleto PDF of the
        invoice
        :return: actions.act_window
        """
        try:
            if not self.file_boleto_pdf_id:
                self._merge_pdf_boletos()

            boleto_id = self.file_boleto_pdf_id
            base_url = self.env['ir.config_parameter'].get_param(
                'web.base.url')
            download_url = '/web/content/%s/%s?download=True' % (
                str(boleto_id.id), boleto_id.name)

            return {
                "type": "ir.actions.act_url",
                "url": str(base_url) + str(download_url),
                "target": "new",
            }
        except Exception as error:
            raise UserError(error)
            # raise error

    def action_invoice_cancel(self):
        try:
            financial_move_line_ids = self.financial_move_line_ids
            if financial_move_line_ids.bank_inter_state == "baixado":
                financial_move_line_ids.drop_bank_slip()
                return super().action_invoice_cancel()
            else:
                raise UserError(
                    _("All Account Move Line related to Invoice must haver their "
                      "status set to 'write off' to be able to cancel.")
                )
        except Exception as error:
            raise UserError(_(error))

    # def create_account_payment_line(self):
    #     res = super().create_account_payment_line()
    #     import pudb;pu.db
    #     if (self.partner_bank_id.bank_id.code_bc == '077' and
    #         self.payment_mode_id.payment_method_id.code == '240'):
    #         self.payment_order_id.draft2open()
    #     return res    
    
    # def action_post(self):
    #     result = super().action_post()
    #     # import pudb;pu.db
    #     # self.load_cnab_info()
    #     self.payment_order_id.draft2open()
    #     return result