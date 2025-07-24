# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


import base64
from odoo import _, models
from odoo.exceptions import UserError
import PyPDF2

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_download_danfe(self):
        if len(self) == 1:
            for order in self:
                invoice = order.invoice_ids.filtered(
                    lambda inv: inv.fiscal_document_id and inv.fiscal_document_id.file_report_id
                )
                if not invoice:
                    raise UserError("Nenhuma DANFE disponível para este pedido de venda.")
                # Pega o primeiro anexo
                attachment = invoice[0].fiscal_document_id.file_report_id
                return {
                    'type': 'ir.actions.act_url',
                    'url': f'/web/content/{attachment.id}?download=true',
                    'target': 'new',
                }
        else:
            merger = PyPDF2.PdfFileMerger()
            danfe = "Danfes"
            for order in self:
                invoices = order.invoice_ids.filtered(
                    lambda inv: inv.fiscal_document_id and inv.fiscal_document_id.file_report_id
                )
                for inv in invoices:
                    attachment = inv.fiscal_document_id.file_report_id
                    merger.append(attachment._full_path(attachment.store_fname))
                    danfe += "_" + inv.fiscal_document_id.document_number
            danfe += ".pdf"
            merger.write("/tmp/" + danfe)
            pdf_file = open("/tmp/" + danfe, "rb")
            attachment = self.env['ir.attachment'].create({
                'name': danfe,
                'datas': base64.b64encode(pdf_file.read()),
                'res_model': 'sale.order',
                'res_id': self[0].id,
                'type': 'binary',
            })
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{attachment.id}?download=true',
                'target': 'new',
            }
