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
        for move_line in self.financial_move_line_ids:
            move_line.generate_pdf_boleto()

    def gera_boleto_pdf(self):
        file_pdf = self.file_boleto_pdf_id
        self.file_boleto_pdf_id = False
        file_pdf.unlink()
        """
        Generates and lists all the attachment ids for an Boleto PDF of the
        invoice
        :return: actions.act_window
        """
        try:
            pay_line = self.env['account.payment.line'].search([('move_id', '=', self.id)])
            if pay_line and not pay_line.date:
                pay_line.order_id.generate_payment_file()

            if not self.file_boleto_pdf_id:
                self._merge_pdf_boletos()
            
            # boleto_id = self.file_boleto_pdf_id
            # base_url = self.env['ir.config_parameter'].get_param(
            #     'web.base.url')
            # download_url = '/web/content/%s/%s?download=True' % (
            #     str(boleto_id.id), boleto_id.name)

            # return {
            #     "type": "ir.actions.act_url",
            #     "url": str(base_url) + str(download_url),
            #     "target": "new",
            # }
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

    def _post(self, soft=True):
        result = super()._post(soft)
        if (self.partner_bank_id.bank_id.code_bc == '077' and
            self.payment_mode_id.payment_method_id.code == '240'
        ):
            if (not self.partner_bank_id.journal_id.bank_inter_id or 
                not self.partner_bank_id.journal_id.bank_inter_secret
            ):
                raise UserError(
                    _("Informe o Id é chave do banco Inter.")
                )
            if self.payment_order_id:
                self.gera_boleto_pdf()
        return result