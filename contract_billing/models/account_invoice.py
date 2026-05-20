# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    email_send = fields.Boolean(string="Email enviado")

    def generate_boleto_pdf(self):
        res = super(AccountMove, self).generate_boleto_pdf()
        if self.file_boleto_pdf_id:
            nome_boleto = self.partner_id.name
            nome_boleto = '_'.join(nome_boleto.split())
            inv_number = self.get_invoice_fiscal_number().split("/")[-1].zfill(6)
            nome_boleto = nome_boleto[:40] + '_' + inv_number
            self.file_boleto_pdf_id.write({'name': f'{nome_boleto}.pdf'})
        return res
