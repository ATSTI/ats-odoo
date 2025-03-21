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
        