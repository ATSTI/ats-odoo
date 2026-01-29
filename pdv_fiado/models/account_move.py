from odoo import models, api, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    pos_extra_note = fields.Char('Dados adicionais (POS)')

    @api.model
    def create_fiado_from_pos(self, partner_id, order_lines, amount_paid):

        move_lines = []
        for line in order_lines:
            move_lines.append((0, 0, {
                'product_id': line['product_id'],
                'quantity': line['quantity'],
                'price_unit': line['price_unit'],
                'tax_ids': [(6, 0, line['tax_ids'])],
            }))

        move = self.env['account.move'].with_context(
            disable_fiscal_document=True
        ).create({
            'move_type': 'out_invoice',
            'partner_id': partner_id,
            'invoice_line_ids': move_lines,
            'fiscal_operation_id': False,
            'document_type_id': False,
        })

        move.action_post()

        payment = False
        if amount_paid and amount_paid > 0:
            journal = self.env['account.journal'].search(
                [('type', '=', 'cash')], limit=1
            )

            payment = self.env['account.payment'].create({
                'payment_type': 'inbound',
                'partner_type': 'customer',
                'partner_id': partner_id,
                'amount': amount_paid,
                'date': fields.Date.context_today(self),
                'journal_id': journal.id,
            })
            payment.action_post()

            invoice_lines = move.line_ids.filtered(
                lambda l: l.account_id.internal_type == 'receivable' and not l.reconciled
            )
            payment_lines = payment.line_ids.filtered(
                lambda l: l.account_id.internal_type == 'receivable' and not l.reconciled
            )

            (invoice_lines + payment_lines).reconcile()

        return {
            'id': move.id,
            'name': move.name,
            'total': move.amount_total,
            'paid': amount_paid,
            'residual': move.amount_residual,
        }
