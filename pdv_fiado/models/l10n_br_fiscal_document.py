from odoo import models, api

class L10nBrFiscalDocument(models.Model):
    _inherit = 'l10n_br_fiscal.document'

    @api.model
    def create(self, vals):
        doc = super().create(vals)

        if doc.move_id and doc.move_id.pos_extra_note:
            doc.manual_customer_additional_data = doc.move_id.pos_extra_note

        return doc
