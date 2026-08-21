from odoo import models, api
from odoo.addons.l10n_br_fiscal.models.document_mixin import FiscalDocumentMixin


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.onchange("document_type_id")
    def _onchange_document_type_id(self):
        for rec in self:
            if not rec.document_type_id:
                continue

            serie = self.env["l10n_br_fiscal.document.serie"].search([
                ("document_type_id", "=", rec.document_type_id.id),
                ("active", "=", True),
            ], limit=1)

            if serie and serie.company_id == rec.company_id:
                rec.document_serie_id = False
                rec.document_number = False

        res = FiscalDocumentMixin._onchange_document_type_id(self)
        # self._onchange_payment_mode_id()
        return res