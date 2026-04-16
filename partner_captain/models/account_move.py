from odoo import models

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_invoice_sent_with_attachments(self):
        self.ensure_one()

        # Chama o comportamento padrão
        action = self.action_invoice_sent()

        attachments = self.env['ir.attachment'].search([
            ('res_model', '=', 'account.move'),
            ('res_id', '=', self.id),
            ('res_field', '=', False),
        ])

        ctx = dict(action.get('context', {}))

        # Pega anexos existentes do template
        existing_ids = []
        if ctx.get('default_attachment_ids'):
            existing = ctx['default_attachment_ids']
            if isinstance(existing, list) and isinstance(existing[0], tuple):
                existing_ids = existing[0][2]

        all_ids = list(set(existing_ids + attachments.ids))

        ctx.update({
            'default_attachment_ids': [(6, 0, all_ids)],
            'default_reply_to': 'financeiro@captaindive.com.br',
        })

        action['context'] = ctx

        return action