from odoo import models
import base64


class FiscalDocument(models.Model):
    _inherit = "l10n_br_fiscal.document"

    def view_pdf(self):
        res = super().view_pdf()

        for doc in self:
            if doc.file_report_id and doc.document_number: #so salva pdf enviado e autorizado com a segunda condicao do document number, 
                #ver se assim funciona, se deixar sem, ele salva o PDF sem ter sido enviado pra receita (antes da autorizacao)
                doc._copy_pdf_to_invoice_attachment()

        return res

    def _copy_pdf_to_invoice_attachment(self):
        self.ensure_one()
        # import pudb;pudb.set_trace()
        invoice = self.env["account.move"].search(
            [("fiscal_document_id", "=", self.id)],
            limit=1,
        )

        if not invoice or not self.file_report_id:
            return

        attachment = self.file_report_id

        vals = {
            "name": attachment.name,
            "res_model": "account.move",
            "res_id": invoice.id,
            "datas": attachment.datas,
            "mimetype": attachment.mimetype,
            "type": "binary",
        }

        existing = self.env["ir.attachment"].search(
            [
                ("res_model", "=", "account.move"),
                ("res_id", "=", invoice.id),
                ("name", "=", attachment.name),
            ],
            limit=1,
        )

        if existing:
            existing.write(vals)
            attachment_id = existing.id
        else:
            attachment_id = self.env["ir.attachment"].create(vals).id

        invoice.message_post(attachment_ids=[attachment_id])