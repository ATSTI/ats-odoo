# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, models, api

class SaleOrder(models.Model):
    _inherit = "sale.order"
   
    # se precisar trocar a operacao do pedido
    # isso corrige a operacao em todas as linhas
    @api.onchange("fiscal_operation_id")
    def _onchange_fiscal_operation_id(self):
        if self.fiscal_operation_id:
            for line in self.order_line:
                line.fiscal_operation_id = self.fiscal_operation_id.id
                line._onchange_fiscal_operation_id()

    @api.onchange("partner_id")
    def _onchange_partner_id_fiscal(self):
        res = super()._onchange_partner_id_fiscal()
        if self.partner_id and self.partner_id.property_account_position_id:
            operation = self.env['l10n_br_fiscal.operation'].search([
                ('fiscal_position_id', '=', self.partner_id.property_account_position_id.id)
            ], limit=1)
            if operation:
                self.fiscal_operation_id = operation.id
        return res