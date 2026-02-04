from odoo import models, api
from odoo.addons.l10n_br_fiscal.constants.fiscal import MODELO_FISCAL_NFCE


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.model
    def _process_order(self, pos_order_vals, draft, existing_order):
        res = super()._process_order(pos_order_vals, draft, existing_order)

        order = self.browse(res)

        # só aplica para NFC-e
        if order.document_type != MODELO_FISCAL_NFCE:
            return res

        move = order.account_move
        if not move:
            return res

        # posta a fatura se necessário
        if move.state == "draft":
            move.action_post()

        # se já está paga, sai
        if move.amount_residual == 0:
            return res

        # cria pagamentos baseados nos pagamentos do POS
        for pos_payment in order.payment_ids:
            journal = pos_payment.payment_method_id.journal_id
            if not journal:
                continue

            pay_vals = {
                "payment_type": "inbound",
                "partner_type": "customer",
                "partner_id": move.partner_id.id,
                "amount": pos_payment.amount,
                "journal_id": journal.id,
                "payment_method_id": self.env.ref(
                    "account.account_payment_method_manual_in"
                ).id,
                "ref": move.name,
            }

            payment = self.env["account.payment"].create(pay_vals)
            payment.action_post()

            lines = (move.line_ids + payment.line_ids).filtered(
                lambda l: l.account_id == payment.destination_account_id
                and not l.reconciled
            )
            lines.reconcile()

        return res
