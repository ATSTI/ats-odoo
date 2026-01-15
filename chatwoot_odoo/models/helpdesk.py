import base64
import os
import requests

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
            additional = sender.get("additional_attributes", {})
            company = additional.get("company_name")
            contact = company if company else sender.get("name")
            termos = contact.split()
            prt = self.find_partner_by_terms(termos)
            if not prt:
                prt = self.env['res.partner'].create({
                    'name': contact,
                    'phone': sender.get("phone_number"),
                })
            if len(prt) > 1:
                prt = prt[0]

            assignee = conv.get("meta", {}).get("assignee", {}).get("name", "Unassigned")
            termos = assignee.split()
            user = self.env['res.users'].search([('name', 'ilike', termos[0])], limit=1)
            if not user:
                user = self.env.ref('base.user_root')

            team = conv.get("meta", {}).get("team", {}).get("name", "Suporte")
            team_rec = self.env['helpdesk.ticket.team'].search([('name', 'ilike', team)], limit=1)
            team_id = team_rec.id if team_rec else False

            messages_data = self.get_message(conversation_id)
            messages = messages_data.get("payload", [])

            mensagem = ""
            attachments_to_create = []

            for msg in messages:
                if msg.get("message_type") == 2:
                    continue

                sender_name = msg.get("sender", {}).get("name", "Sistema")
                content = msg.get("content") or ""
                mensagem += f"\n{sender_name}: {content}\n"

                for att in msg.get("attachments", []):
                    data_url = att.get("data_url")
                    if not data_url:
                        continue

                    filename = data_url.split("/")[-1]
                    file_content = requests.get(data_url, headers=HEADERS).content
                    mensagem += f"\n[Anexo: {filename}]\n"
                    attachments_to_create.append({
                        'name': filename,
                        'datas': base64.b64encode(file_content),
                        'res_model': 'helpdesk.ticket',
                    })

            ticket = self.env['helpdesk.ticket'].create({
                'name': f"Chatwoot - {contact}",
                'description': mensagem,
                'partner_id': prt.id,
                'user_id': user.id,
                'chatwoot_conversation_id': f"{conversation_id}2026",
                'team_id': team_id,
            })

            for att in attachments_to_create:
                att['res_id'] = ticket.id
                self.env['ir.attachment'].create(att)

    def download_file(self, data_url, filename):
        response = requests.get(data_url, headers=HEADERS)
        response.raise_for_status()

        with open(filename, "wb") as f:
            f.write(response.content)

        print("Arquivo salvo:", filename)

    def get_unique_conversation(self, conversation_id):
        url_conversation = f"{BASE_URL}/api/v1/accounts/{ACCOUNT_ID}/conversations/{conversation_id}"
        response_conversation = requests.get(url_conversation, headers=HEADERS)
        return response_conversation.json()

    def get_message(self, conversation_id):
        url_message = f"{BASE_URL}/api/v1/accounts/{ACCOUNT_ID}/conversations/{conversation_id}/messages"
        response_message = requests.get(url_message, headers=HEADERS)
        return response_message.json()

    
    def find_partner_by_terms(self, termos):
        Partner = self.env["res.partner"]

        for i in range(len(termos), 0, -1):
            texto = " ".join(termos[:i])
            res = Partner.search([("name", "ilike", texto)])
            if res and len(res) == 1:
                return res

        domain = []
        for termo in termos:
            if domain:
                domain = ["|"] + domain
            domain.append(("name", "ilike", termo))

        return Partner.search(domain)