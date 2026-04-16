from odoo import models, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_send_email_with_attachments(self):
        self.ensure_one()

        template = self.env.ref('account.email_template_edi_invoice', raise_if_not_found=False)

        attachments = self.env['ir.attachment'].search([
            ('res_model', '=', 'account.move'),
            ('res_id', '=', self.id),
            ('res_field', '=', False),
        ])

        ctx = {
            'default_model': 'account.move',
            'default_res_id': self.id,
            'default_use_template': bool(template),
            'default_template_id': template.id if template else False,
            'default_composition_mode': 'comment',
            'default_attachment_ids': [(6, 0, attachments.ids)],
            'default_email_layout_xmlid': 'mail.mail_notification_paynow',
            'force_email': True,
            'default_reply_to': 'financeiro@captaindive.com.br',
        }

        return {
            'name': 'Enviar Fatura por Email',
            'type': 'ir.actions.act_window',
            'res_model': 'mail.compose.message',
            'view_mode': 'form',
            'target': 'new',
            'context': ctx,
        }