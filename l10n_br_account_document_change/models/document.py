# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class FiscalDocumentTransp(models.Model):
    _inherit = "l10n_br_fiscal.document"

    def action_back_account(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "views": [[False, "form"]],
            "res_id": self.move_ids.id,
            "context": {},
        }
    
    def action_document_confirm(self):
        if self.move_ids.fatura_duplicata == False:
            if self.nfe40_dup:
                self.nfe40_dup.unlink()
        result = super().action_document_confirm()
        return result
        
    def action_document_send(self):
        if self.move_ids.fatura_duplicata == False:
            if self.nfe40_dup:
                self.nfe40_dup.unlink()
        result = super().action_document_send()
        return result