# -*- coding: utf-8 -*-
from odoo import models, api, _, fields
from odoo.exceptions import UserError
import os
import base64
import io
import glob
from PyPDF2 import PdfFileReader, PdfFileMerger


class AccountInvoicePrint(models.TransientModel):
    """
    This wizard will confirm the all the selected draft invoices
    """

    _name = "account.invoice.print"
    _description = "Imprime todos os boletos"
    
    arq_file = fields.Binary(string=u"Arquivo PDF")
    arq_file_name = fields.Char(
        string=u"Arquivo PDF")

    def mostra_pdf(self):
        # def gera_um_pdf(self):
        self.mostra_pdf()
        my_file = self.env['accont.invoice.print'].create({
             'file_name': 'boletos.pdf',
             'pdf_file': self.arq_file,
        })
        return {
            'name': _('Download File'),
            'res_id': my_file.id,
            'res_model': 'account.invoice.print',
            'target': 'new',
            'type': 'ir.actions.act_window',
            'view_id': self.env.ref('account_invoice_print.account_invoice_print_view').id,
            'view_mode': 'form',
            'view_type': 'form',
            }

    @api.multi
    def gera_um_pdf(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        files_dir = '/home/odoo/pdf/'
        files = glob.glob(os.path.join(files_dir + '*.pdf'))
        for file_rem in files:
            os.remove(file_rem)
        for record in self.env['account.invoice'].browse(active_ids):
            attachment_ids = self.env['ir.attachment'].search(
                [('res_model', '=', 'account.invoice'),
                 ('res_id', '=', record.id),
                 ('name', 'ilike', 'boleto'),
                 ])

            if len(attachment_ids) > 1:
                msg = 'Existe dois anexos na fatura(id) %s' %(record.id)
                raise UserError(_(msg))
            arq = files_dir + attachment_ids.name
            arquivo = open(arq, 'wb')
            #arquivo.write(attachment_ids.datas)
            arquivo.write(base64.b64decode(attachment_ids.datas))
            arquivo.close()
            
            #try:
            #    report_invoice = record.env['ir.actions.report']._get_report_from_name('br_boleto.report.print')
            #except IndexError:
            #    report_invoice = False
            #if report_invoice and report_invoice.attachment:
            #    for invoice in record:
            #        attachment = self.env.ref('account.account_invoices').retrieve_attachment(invoice)
            #    if attachment:
            #        x = 'tem arquivo aqui'
        # juntando tudo em um PDF
        pdf_files = [f for f in os.listdir(files_dir) if f.endswith('pdf')]
        merger = PdfFileMerger()
        for filename in pdf_files:
            merger.append(PdfFileReader(os.path.join(files_dir, filename), 'rb'))
        merger.write(os.path.join(files_dir, 'boletos.pdf'))
        arq = files_dir + 'boletos.pdf'
        arquivo = open(arq, 'rb')
        BinaryArq = base64.b64encode(arquivo.read())
        #BytesArq = BinaryArq.data
        #ArqBase64 = base64.b64encode(BytesArq)
        #eSend = ImageBase64.decode('ascii')
        #tmpPDF = io.BytesIO()
        #arquivo.writeto_pdf(tmpPDF)
        self.arq_file_name = files_dir + 'boleto.pdf'
        self.arq_file = BinaryArq
        arquivo.close()
        return {
                'type': 'ir.actions.do_nothing',
            }
