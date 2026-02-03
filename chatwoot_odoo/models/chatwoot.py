import base64
import requests
import io
import mimetypes
import os
from odoo import models, fields

class ChatwootInstance(models.Model):
    _name = 'chatwoot.instance'
    _description = 'Chatwoot Instance'

    base_url = fields.Char(
        string="Base URL",
        help="URL base do Chatwoot"
    )

    code = fields.Char(
    string="Código Técnico",
    required=True,
    help="Chave usada para mapear o usuário no selection"
)
    name = fields.Char(required=True)

    api_token = fields.Char(
        string="API Token",
        help="Token de acesso à API do Chatwoot"
    )
    account_id = fields.Char(
        string="Account ID",
        default="1",
        help="ID da conta do Chatwoot"
    )

    def get_contact_id(self, phone_number, partner):
        url = f"{self.base_url}/api/v1/accounts/{self.account_id}/contacts/search"
        params = {
            "q": phone_number,
            "page": 1,
        }
        headers = {
            "api_access_token": self.api_token
        }
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        contacts = data.get("payload", [])
        if contacts:
            return contacts[0].get("id")
        else:
            payload = {
                "name": partner.name,
                "phone_number": phone_number
            }
            create_response = requests.post(
                f"{self.base_url}/api/v1/accounts/{self.account_id}/contacts",
                json=payload,
                headers=headers
            )
            created_data = create_response.json()
            id = created_data.get("payload", {}).get("contact", {}).get("id")
            if id:
                return id
            else:
                raise Exception(f"Impossivel Criar Contato no Chatwoot") 

    def create_new_conversation(self, phone_number, partner, team_id, assignee_id):
        #TODO Ainda não sei como tratar a conversa, ideias: Busca pela conversa aberta para aquele contato ou
        # criar uma nova conversa sempre e fecha-la depois de enviar a mensagem, o que obriga o user a enviar tudo que for necessário de uma vez só.
        url = f"{self.base_url}/api/v1/accounts/{self.account_id}/conversations"
        payload = {
            "contact_id": self.get_contact_id(phone_number, partner),
            "source_id": phone_number,
            "inbox_id": 5,
            "team_id": int(team_id),
            "assignee_id": int(assignee_id),
            "status": "open",
            # "message": {
            #     "content": content,
            # }
        }
        headers = {
            "api_access_token": self.api_token,
            "Content-Type": "application/json"
        }
        response = requests.post(url, json=payload, headers=headers)
        return response.json()
    
    def get_unique_conversation(self, conversation_id):
        url_conversation = f"{self.base_url}/api/v1/accounts/{self.account_id}/conversations/{conversation_id}"
        headers = {
            "api_access_token": self.api_token
        }
        response_conversation = requests.get(url_conversation, headers=headers)
        return response_conversation.json()

    def get_message(self, conversation_id):
        url_message = f"{self.base_url}/api/v1/accounts/{self.account_id}/conversations/{conversation_id}/messages"
        headers = {
            "api_access_token": self.api_token
        }
        response_message = requests.get(url_message, headers=headers)
        return response_message.json()

    def set_resolved_conversation(self, conversation_id):
        url = f"{self.base_url}/api/v1/accounts/{self.account_id}/conversations/{conversation_id}/toggle_status"
        payload = {
            "status": "resolved",
        }
        headers = {
            "api_access_token": self.api_token,
        }
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        if response.status_code != 200:
            raise Exception(f"Failed to resolve conversation {conversation_id}: {response.text}")
        else:
            return True

    def send_text(self, conversation_id, message):
        url = f"{self.base_url}/api/v1/accounts/{self.account_id}/conversations/{conversation_id}/messages"
        payload = {
            "content": message,
        }
        headers = {
            "api_access_token": self.api_token,
        }
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        return response.json()

    def send_chatwoot_attachment(self, conversation_id, attachment, message=None):
        file_content = base64.b64decode(attachment.datas)
        file_stream = io.BytesIO(file_content)

        filename = attachment.name or "arquivo"

        if "." not in filename:
            filename += ".pdf"

        mimetype = attachment.mimetype
        if not mimetype:
            mimetype, _ = mimetypes.guess_type(filename)

        if not mimetype:
            mimetype = "application/pdf"

        url = f"{self.base_url}/api/v1/accounts/{self.account_id}/conversations/{conversation_id}/messages"
        headers = {
            "api_access_token": self.api_token
        }

        files = {
            "attachments[]": (
                filename,
                file_stream,
                mimetype
            )
        }

        data = {}
        if message:
            data["content"] = message

        response = requests.post(
            url,
            headers=headers,
            data=data,
            files=files,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def add_label_to_conversation(self, conversation_id):
        url = f"{self.base_url}/api/v1/accounts/{self.account_id}/conversations/{conversation_id}/labels"
        payload = {
            "labels": [
                "start_conversation"
            ]
        }
        headers = {
            "api_access_token": self.api_token,
        }
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        return response.json()