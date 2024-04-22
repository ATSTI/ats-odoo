# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, models, api

class AccountMove(models.Model):
    _name = "account.move"
    _inherit = [
        _name,
        "l10n_br_fiscal.document.move.mixin",
    ]
    _inherits = {"l10n_br_fiscal.document": "fiscal_document_id"}
    _order = "date DESC, name DESC"
    
    @api.onchange("fiscal_operation_id")
    def _onchange_fiscal_operation_id(self):
        result = super()._onchange_fiscal_operation_id()
        self._compute_amount()
        for line in self.invoice_line_ids:
            line.fiscal_operation_id = self.fiscal_operation_id
            line._onchange_fiscal_operation_id()
            line._onchange_price_subtotal()
        
        self._recompute_dynamic_lines(recompute_all_taxes=True)
        self._recompute_payment_terms_lines()
        return result
     