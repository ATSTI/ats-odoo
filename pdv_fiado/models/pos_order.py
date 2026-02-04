from odoo import models, api
from odoo.addons.l10n_br_fiscal.constants.fiscal import MODELO_FISCAL_NFCE


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.model
    def _process_order(self, pos_order_vals, draft, existing_order):
        res = super()._process_order(pos_order_vals, draft, existing_order)

        order = self.browse(res)

        if order.document_type != MODELO_FISCAL_NFCE:
            return res

        move = order.account_move
        if not move:
            return res

        if move.state == "draft":
            move.action_post()

        # já pago → sai
        if move.amount_residual == 0:
            return res

        # 🔹 reconciliar linhas de pagamento do POS com a fatura
        receivable_lines = move.line_ids.filtered(
            lambda l: l.account_internal_type == "receivable" and not l.reconciled
        )

        pos_payment_lines = order.account_move.line_ids.filtered(
            lambda l: l.account_internal_type == "receivable" and not l.reconciled
        )

        lines = receivable_lines | pos_payment_lines

        if lines:
            lines.reconcile()

        return res
