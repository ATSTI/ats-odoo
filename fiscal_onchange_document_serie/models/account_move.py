from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = "account.move"

    @api.onchange("document_type")
    def _onchange_document_type(self):
        for rec in self:
            if rec.document_type_id:
                domain = self.env['l10n_br_fiscal.document.serie'].search([('document_type_id', '=', rec.document_type_id.id, 'active', '=', True)])
                if domain:
                    rec.document_serie_id = domain[0]