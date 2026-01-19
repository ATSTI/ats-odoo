import base64
import os
import re
import requests
import unicodedata

from dotenv import load_dotenv
from odoo import models, fields

load_dotenv()

BASE_URL = os.getenv("CHATWOOT_BASE_URL")
API_TOKEN = os.getenv("CHATWOOT_API_TOKEN")
ACCOUNT_ID = os.getenv("CHATWOOT_ACCOUNT_ID")

HEADERS = {
    "api_access_token": API_TOKEN
}

if not BASE_URL or not API_TOKEN or not ACCOUNT_ID:
    raise ValueError("Configuração Chatwoot inválida. Verifique o arquivo .env")

class HelpDeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    chatwoot_conversation_id = fields.Char(
        string="Protocolo Chatwoot",
        help="ID da conversa associada no Chatwoot"
    )

    def get_conversations_resolved(self):
        url = f"{BASE_URL}/api/v1/accounts/{ACCOUNT_ID}/conversations"
        params = {
            "assignee_type": "all",
            "status": "resolved",
            "page": 1,
        }

        response = requests.get(url, headers=HEADERS, params=params, timeout=30)
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
            
            assignee = self.get_unique_conversation(conversation_id).get("meta", {}).get("assignee", {}).get("name", "Unassigned")
            termos = assignee.split()
            user = self.env['res.users'].search([('name', 'ilike', termos[0])], limit=1)

            team = conv.get("meta", {}).get("team", {}).get("name", "Suporte")
            team_rec = self.env['helpdesk.ticket.team'].search([('name', 'ilike', team)], limit=1)
            team_id = team_rec.id if team_rec else False

            messages_data = self.get_message(conversation_id)
            messages = messages_data.get("payload", [])

            mensagem = ""
            user_name = ""
            attachments_to_create = []

            for msg in messages:
                content = msg.get("content") or ""
                if msg.get("message_type") == 2:
                    if not user and content:
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
                    file_content = requests.get(data_url, headers=HEADERS).content
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
            })
            if prt.id == 1:
                ticket.partner_name = contact + " (COLOCAR PARCEIRO CORRETO)"
            else:
                ticket._onchange_partner_id()

            for att in attachments_to_create:
                att['res_id'] = ticket.id
                self.env['ir.attachment'].create(att)

    def get_unique_conversation(self, conversation_id):
        url_conversation = f"{BASE_URL}/api/v1/accounts/{ACCOUNT_ID}/conversations/{conversation_id}"
        response_conversation = requests.get(url_conversation, headers=HEADERS)
        return response_conversation.json()

    def get_message(self, conversation_id):
        url_message = f"{BASE_URL}/api/v1/accounts/{ACCOUNT_ID}/conversations/{conversation_id}/messages"
        response_message = requests.get(url_message, headers=HEADERS)
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
            prt = Partner.search(['|', ('name', 'ilike', contact), ('phone_sanitized', 'ilike', phone)], limit=1)
        if not prt:
            contact = contact[contact.find(" - ") + 1:] if " - " in contact else contact
            prt = Partner.search(['|', ('name', 'ilike', contact), ('phone_sanitized', 'ilike', phone)], limit=1)
        if not prt:
            prt = Partner.browse(1)
        return prt