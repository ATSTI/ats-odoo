from odoo import models, fields, api
import requests

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
                #import pudb;pudb.set_trace()
                odoobot = self.env['res.partner'].search([('name','ilike','odoobot'), ('active', '=', False)], limit=1)
                if msg.author_id != odoobot:
                    user_content = str(msg.body).replace('<p>','').replace('</p>','').strip()
                    category = self._classify_message(user_content)
                    if category == 'outro':
                        openai = self.env['ai.bridge'].search([('name','=', 'OpenAI')], limit = 1)
                    else:
                        openai = self.env['ai.bridge'].search([('name','ilike', category)], limit = 1)
                    if openai:
                        model = openai.model
                        ids = self.env[model].search(eval(openai.domain)).ids
                        openai.execute_ai_bridge(str(model), ids, user_content)
        return messages
    
    def _classify_message(self, content):
        """
        Usa OpenAI para classificar a mensagem em: crm, fatura ou outro #Adicionar outras classes
        """
        openai = self.env['ai.bridge'].search([], limit = 1)
        api_key = openai.auth_token
        url = "https://api.openai.com/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": "gpt-4o-mini",   # pode ser gpt-4o-mini ou gpt-5
            "messages": [
                {"role": "system", "content": "Você é um classificador. Responda apenas com uma das opções: crm, fatura, outro."},
                {"role": "user", "content": content}
            ],
            "temperature": 0
        }

        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()

        category = data["choices"][0]["message"]["content"].strip().lower()
        return category
