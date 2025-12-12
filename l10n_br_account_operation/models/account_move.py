# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, models, api

class AccountMove(models.Model):
    _inherit = "account.move"
   
    # quando o cliente emite somente nota, acontece de precisar trocar a operacao
    # isso corrige a operacao em todas as linhas da fatura
    @api.onchange("fiscal_operation_id")
    def _onchange_fiscal_operation_id(self):
        # import pudb;pu.db
        if self.fiscal_operation_id:
            for line in self.invoice_line_ids:
                line.fiscal_operation_id = self.fiscal_operation_id.id
                line._compute_all_tax()
                line._compute_fiscal_amounts()

    @api.onchange("partner_id")
    def _onchange_partner_id_fiscal(self):
        partner = self.partner_id
        if partner and partner.property_account_position_id:
            operation = self.env['l10n_br_fiscal.operation'].search([
                ('fiscal_position_id', '=', partner.property_account_position_id.id)
            ], limit=1)
            if operation:
                self.fiscal_operation_id = operation.id
            self.ind_final = partner.ind_final
            for line in self._get_amount_lines():
                # reload fiscal data, operation line, cfop, taxes, etc.
                line._onchange_fiscal_operation_id()