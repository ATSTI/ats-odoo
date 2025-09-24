from odoo import models, fields, api

class MailMessage(models.Model):
    _inherit = "mail.message"

    @api.model_create_multi
    def create(self, values_list):
        import pudb;pudb.set_trace()
        messages = super().create(values_list)

        openai_channel = self.env['mail.channel'].search([('name','ilike','OpenAi')], limit=1)
        if not openai_channel:
            return messages

        for msg in messages:
            if msg.model == 'mail.channel' and msg.res_id == openai_channel.id:
                if msg.author_id.name.lower() != 'odoobot':
                    user_content = ''
                    openai = self.env['ai.bridge'].search([('name','ilike','openai')], limit = 1)
                    if openai:   
                        self.env['ai.bridge'].execute_ai_bridge('crm.lead', None, user_content)
        return messages
