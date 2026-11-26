from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    payment_date = fields.Date(
        string='Data de Pagamento',
        compute='_compute_payment_date',
        store=True,
    )

    @api.depends(
        'payment_state',
        'line_ids.matched_debit_ids.max_date',
        'line_ids.matched_credit_ids.max_date',
    )
    def _compute_payment_date(self):
        for move in self:
            payment_date = False
            if move.is_invoice(include_receipts=True) and move.payment_state in ('paid', 'in_payment'):
                term_lines = move.line_ids.filtered(lambda l: l.display_type == 'payment_term')
                partials = term_lines.matched_debit_ids | term_lines.matched_credit_ids
                dates = []
                for partial in partials:
                    counterpart = (
                        partial.debit_move_id
                        if partial.credit_move_id in term_lines
                        else partial.credit_move_id
                    )
                    dates.append(counterpart.date)
                payment_date = max(dates) if dates else False
            move.payment_date = payment_date