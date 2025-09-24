# -*- coding: utf-8 -*- © 2017 Carlos R. Silveira, ATSti
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json
import traceback
from datetime import timedelta
from io import StringIO

import requests
from werkzeug import urls

from odoo import _, api, fields, models, tools

class AiBridge(models.Model):
    _inherit = "ai.bridge"

    #funcao _prepare_payload

    def execute_ai_bridge(self, res_model, res_id, user_content):
        self.ensure_one()
        if not self.active or (
            self.group_ids and not self.env.user.groups_id & self.group_ids
        ):
            return {
                "body": _("%s is not active.", self.name),
                "args": {"type": "warning", "title": _("AI Bridge Inactive")},
            }
        record = self.env[res_model].browse(res_id).exists()
        if record:
            execution = self.env["ai.bridge.execution"].create(
                {
                    "ai_bridge_id": self.id,
                    "model_id": self.sudo().env["ir.model"]._get_id(res_model),
                    "res_id": res_id,
                }
            )
            result = execution._execute(user_content)
            if result:
                return result
            if execution.state == "done":
                return {
                    "notification": {
                        "body": _("%s executed successfully.", self.name),
                        "args": {"type": "success", "title": _("AI Bridge Executed")},
                    }
                }
            return {
                "notification": {
                    "body": _("%s failed.", self.name),
                    "args": {"type": "danger", "title": _("AI Bridge Failed")},
                }
            }

    def _prepare_payload_record(self, record=None, **kwargs):
        """Prepare the payload to be sent to the AI system."""
        self.ensure_one()
        if not self.model_id:
            return {}
        if record is None and self.env.context.get("sample_payload"):
            record = self.env[self.model_id.model].search([],)
            if not record or not record.exists():
                return {}

        if record and self.sudo().field_ids:
            user_content =""
            if self.sudo().field_ids:
                field_names = self.sudo().field_ids.mapped('name')
                read_vals = record.read(field_names)
                if read_vals:
                    vals = read_vals[0]
                    #transforma em string legivel
                    for key, value in vals.items():
                        user_content += f"{key}: {value}\n"

            if not user_content.strip():
                user_content='Sem dados disponiveis do registro'
        else:
            channel = self.env['mail.channel'].search([('name', 'ilike', 'OpenAi')], limit=1)
            last_message = self.env['mail.message'].search([('res_id', '=', channel.id),('author_id','!=','OdooBot')], order='id desc', limit=1) if channel else None
            user_content = (last_message.body.replace("\n", " ") if last_message else "Sem instrução disponível.")

        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "Você é um assistente para leads de CRM."},
                {"role": "user", "content": user_content}
            ]
        }

        # self.chatOpenAi() 
        return payload
        #falta fazer executar a ponte apos enviar a mensagem no canal
    
    def chatOpenAi(self):
        # import pudb;pudb.set_trace()
        openai = self.env['ai.bridge'].search([('name','ilike','openai')], limit = 1)
        for chat in openai:
            chat.execute_ai_bridge(res_model = 'crm.lead', res_id = 651)




    
   
class AiBridgeExecution(models.Model):

    _inherit = "ai.bridge.execution"


    def _execute(self, user_content,**kwargs):
        self.ensure_one()
        record = None
        if self.res_id and self.model_id:
            record = self.env[self.sudo().model_id.model].browse(self.res_id)
        payload = self.ai_bridge_id._prepare_payload_record(user_content)
        try:
            response = requests.post(
                self.ai_bridge_id.url,
                json=payload,
                auth=self._get_auth(),
                headers=self._get_headers(),
                timeout=30,  # Default timeout, can be overridden by _execute_kwargs
                **self._execute_kwargs(**kwargs),
            )
            self.result = response.content
            response.raise_for_status()
            self.state = "done"
            self.payload = payload
            if self.ai_bridge_id.result_kind == "immediate":
                return self._process_response(response.json())
        except Exception:
            self.state = "error"
            self.payload = payload
            buff = StringIO()
            traceback.print_exc(file=buff)
            self.error = buff.getvalue()
            buff.close()


    def _process_response_message(self, response): #feito e funcionando
        import pudb;pudb.set_trace()
        try:
            content = response.get("choices", [])[0].get("message", {}).get("content", "⚠️ Resposta vazia")
            channel = self.env['mail.channel'].search([('name', 'ilike', 'OpenAi')], limit=1)
            if not channel:
                return {"error": "Canal 'OpenAi' não encontrado."}


            odoo_bot_user = self.env['res.users'].search([('login', 'ilike', 'OdooBot')], limit=1)
            author_id = odoo_bot_user.partner_id.id if odoo_bot_user else self.env.user.partner_id.id

            msg_id = channel.message_post(
            body=content.replace("\n", "<br>"),  # evita quebras de linha no chat
            message_type='comment',
            subtype_xmlid='mail.mt_comment',
            author_id=author_id  # pode usar OdooBot se quiser
        ).id

            return {"id": msg_id}

        except Exception as e:
            return {"error": str(e), "raw_response": response}


       
#funcao _response_message




class AiBridgeThread(models.AbstractModel):
    _inherit = "ai.bridge.thread"