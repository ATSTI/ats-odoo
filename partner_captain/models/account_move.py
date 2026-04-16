from odoo import models

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_invoice_sent(self):
        action = super().action_invoice_sent()

        if self:
            attachments = self.env['ir.attachment'].search([
                ('res_model', '=', 'account.move'),
                ('res_id', 'in', self.ids),
            ])

            ctx = dict(action.get('context', {}))
            ctx.update({
                'default_attachment_ids': [(6, 0, attachments.ids)],
                'default_reply_to': 'financeiro@captaindive.com.br',
            })

            action['context'] = ctx

        return action