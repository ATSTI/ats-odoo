import base64
import re
import requests
import unicodedata

from odoo import models, fields


class HelpDeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    chatwoot_conversation_id = fields.Char(
        string="Protocolo Chatwoot",
        help="ID da conversa associada no Chatwoot"
    )

    chatwoot_id = fields.Many2one(
        'chatwoot.instance', 
        string="Instância",
        domain=[('account_id', '=', "1")],
    )

    def get_conversations_resolved(self):
        self.chatwoot_id = self.env['chatwoot.instance'].search(["account_id", "=", "1"], limit=1)
        url = f"{self.chatwoot_id.base_url}/api/v1/accounts/{self.chatwoot_id.account_id}/conversations"
        headers = {
            "api_access_token": self.chatwoot_id.api_token
        }
        params = {
            "assignee_type": "all",
            "status": "resolved",
            "page": 1,
        }

        response = requests.get(url, headers=headers, params=params, timeout=30)
        if response.status_code != 200:
            return


        data = response.json()
        conversations = data.get("data", {}).get("payload", [])

        for conv in conversations:
            conversation_id = conv.get("id")
            conversa = self.env['helpdesk.ticket'].search(
                [('chatwoot_conversation_id', '=', f"{conversation_id}2026")],
                limit=1
            )
            if conversa:
                continue

            sender = conv.get("meta", {}).get("sender", {})
            company = sender.get("additional_attributes", {}).get("company_name")
            contact = company if company else sender.get("name")
            phone = sender.get("phone_number").replace("+", "")
            prt = self.get_partner(contact, phone)

            team = conv.get("meta", {}).get("team", {}).get("name")
            if team != "suporte":
                continue
            team_rec = self.env['helpdesk.ticket.team'].search([('name', 'ilike', team)], limit=1)
            team_id = team_rec.id if team_rec else False

            messages_data = self.get_message(conversation_id)
            messages = messages_data.get("payload", [])

            mensagem = ""
            user_name = ""
            attachments_to_create = []
            messages_type_1 = [msg for msg in messages if msg.get("message_type") == 1]

            for msg in messages:
                content = msg.get("content") or ""

                if messages_type_1 and messages_type_1[len(messages_type_1)-1] == msg:
                    ignore = re.search(r"Ou digite \"encerrar\" para finalizar o atendimento", content, re.IGNORECASE)
                    if ignore:
                        return True

                if msg.get("message_type") == 2:
                    if not user_name and content:
                        match = re.search(r"resolvida por\s+(.*)$", content, re.IGNORECASE)
                        if match:
                            user_name = match.group(1).strip()
                    continue

                sender_name = msg.get("sender", {}).get("name", "Sistema")
                mensagem += f"{sender_name}: {content}<br/>"

                for att in msg.get("attachments", []):
                    data_url = att.get("data_url")
                    if not data_url:
                        continue

                    filename = data_url.split("/")[-1]
                    file_content = requests.get(data_url, headers=headers).content
                    mensagem += f"[Anexo: {filename}]<br/>"
                    attachments_to_create.append({
                        'name': filename,
                        'datas': base64.b64encode(file_content),
                        'res_model': 'helpdesk.ticket',
                    })
            user = self.env['res.users'].search([('name', 'ilike', user_name)], limit=1) if user_name else user
            if not user:
                user = self.env.ref('base.user_root')
            ticket = self.env['helpdesk.ticket'].create({
                'name': f"Chatwoot - {contact}",
                'description': mensagem,
                'partner_id': prt.id,
                'user_id': user.id,
                'chatwoot_conversation_id': f"{conversation_id}2026",
                'team_id': team_id,
                'channel_id': 5,  # Suporte WhatsApp
                'stage_id': 4,  # Concluido
            })
            if prt.id == 1:
                ticket.partner_name = contact + " (COLOCAR PARCEIRO CORRETO)"
            else:
                ticket._onchange_partner_id()

            for att in attachments_to_create:
                att['res_id'] = ticket.id
                self.env['ir.attachment'].create(att)

    def get_unique_conversation(self, conversation_id):
        url_conversation = f"{self.chatwoot_id.base_url}/api/v1/accounts/{self.chatwoot_id.account_id}/conversations/{conversation_id}"
        headers = {
            "api_access_token": self.chatwoot_id.api_token
        }
        response_conversation = requests.get(url_conversation, headers=headers)
        return response_conversation.json()

    def get_message(self, conversation_id):
        url_message = f"{self.chatwoot_id.base_url}/api/v1/accounts/{self.chatwoot_id.account_id}/conversations/{conversation_id}/messages"
        headers = {
            "api_access_token": self.chatwoot_id.api_token
        }
        response_message = requests.get(url_message, headers=headers)
        return response_message.json()

    def remove_acentos(self, texto):
        if not texto:
            return texto
        return ''.join(
            c for c in unicodedata.normalize('NFKD', texto)
            if not unicodedata.combining(c)
        )

    def get_partner(self, contact, phone):
        Partner = self.env['res.partner']
        prt = Partner.search(['|', ('name', 'ilike', self.remove_acentos(contact)), ('phone_sanitized', 'ilike', phone)], limit=1)
        if not prt:
            prt = Partner.search([('name', 'ilike', contact)], limit=1)
        if not prt:
            contact_p = contact[contact.find(" - ") + 3:] if " - " in contact else contact
            prt = Partner.search([('name', 'ilike', contact_p)], limit=1)
        if not prt:
            termos = contact.split()
            domain = []
            for termo in termos:
                if domain:
                    domain = ["|"] + domain
                domain.append(("name", "ilike", termo))
            prt = Partner.search(domain)
            if prt and len(prt) > 1 and len(prt) <= 3:
                prt = prt[0]
        if not prt or len(prt) > 1:
            prt = Partner.browse(1)
        return prt