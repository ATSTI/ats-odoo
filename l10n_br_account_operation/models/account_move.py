# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, models, api

class AccountMove(models.Model):
    _inherit = "account.move"
   
    # quando o cliente emite somente nota, acontece de precisar trocar a operacao
    # isso corrige a operacao em todas as linhas da fatura
    @api.onchange("fiscal_operation_id")
    def _onchange_fiscal_operation_id(self):
        if self.fiscal_operation_id:
            for line in self.invoice_line_ids:
                line.fiscal_operation_id = self.fiscal_operation_id.id
                # corrige o parceiro da linha fiscal, caso seja diferente do parceiro da fatura
                # isso gera problema se ele for outro uf nao carrega o cfop correto
                if line.fiscal_document_line_id.partner_id != self.partner_id:
                    line.fiscal_document_line_id.partner_id = self.partner_id
                line._compute_all_tax()
