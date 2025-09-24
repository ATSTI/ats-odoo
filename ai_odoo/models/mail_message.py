from odoo import models, fields, api

class MailMessage(models.Model):
    _inherit = "mail.message"

    @api.model_create_multi
    def create(self, values_list):
        messages = super().create(values_list)

        openai_channel = self.env['mail.channel'].search([('name','ilike','OpenAi')], limit=1)
        if not openai_channel:
            return messages

        for msg in messages:
            if msg.model == 'mail.channel' and msg.res_id == openai_channel.id:
                import pudb;pudb.set_trace()
                odoobot = self.env['res.partner'].search([('name','ilike','odoobot'), ('active', '=', False)], limit=1)
                if msg.author_id != odoobot:
                    user_content = str(msg.body).replace('<p>','').replace('</p>','').strip()
                    openai = self.env['ai.bridge'].search([('name','ilike','openai')], limit = 1)
                    if openai:
                        model = openai.model
                        ids = self.env[model].search(eval(openai.domain)).ids
                        openai.execute_ai_bridge(str(model), ids, user_content)
        return messages
