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

    def execute_ai_bridge(self, res_model, res_id, user_content):
        self.ensure_one()
        

        if not self.active or (
            self.group_ids and not self.env.user.groups_id & self.group_ids
        ):
            return {
                "body": _("%s is not active.", self.name),
                "args": {
                    "type": "warning",
                    "title": _("AI Bridge Inactive"),
                },
            }

        record = False
        if res_id:
            record = self.env[res_model].browse(res_id).exists()
        execution = self.env["ai.bridge.execution"].create({
            "ai_bridge_id": self.id,
            "model_id": self.sudo().env["ir.model"]._get_id(res_model),
        })
        result = execution._execute(user_content, res_id)
        if result:
            return result

        if execution.state == "done":
            return {
                "notification": {
                    "body": _("%s executed successfully.", self.name),
                    "args": {
                        "type": "success",
                        "title": _("AI Bridge Executed"),
                    },
                }
            }

        return {
            "notification": {
                "body": _("%s failed.", self.name),
                "args": {
                    "type": "danger",
                    "title": _("AI Bridge Failed"),
                },
            }
        }

    def _prepare_payload_record(self, user_content=None, record=None, **kwargs):
        # import pudb;pu.db
        """Prepare the payload to be sent to the AI system."""
        self.ensure_one()
        if not self.model_id:
            return {}

        # Se não veio user_content, tenta montar pelo record
        if not user_content:
            if record is None and self.env.context.get("sample_payload"):
                record = self.env[self.model_id.model].search([], limit=1)
                user_content = ""
                campos = ""
                if not record or not record.exists():
                    return {}
        campos = ""
        if record and self.sudo().field_ids:
            field_names = self.sudo().field_ids.mapped("name")
            for modelo in record.read(field_names):
                vals = modelo

                if vals:
                    for key, value in vals.items():
                        if isinstance(value, tuple):  # Many2one
                            value = value[1]
                        elif isinstance(value, bool):
                            value = "Sim" if value else "Não"
                        elif isinstance(value, list):
                            value = ", ".join(str(v) for v in value)
                        campos += f"{key}: {value}\n"

            if not campos.strip():
                campos = "Sem dados disponíveis do registro"
        funcao = self.description if self.description else "Você é um assistente de um ERP"
        if campos:
            info = f"Dados da respectiva classe: {campos}"
        else:
            info = ""
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": funcao},
                {"role": "user", "content": user_content + info or "Sem conteúdo"},
            ],
        }

        return payload
    
   
class AiBridgeExecution(models.Model):

    _inherit = "ai.bridge.execution"


    def _execute(self, user_content, res_id,**kwargs):
        self.ensure_one()
        record = None
        if res_id and self.model_id:
            record = self.env[self.sudo().model_id.model].browse(res_id)
        payload = self.ai_bridge_id._prepare_payload_record(user_content, record=record, **kwargs)
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
        try:
            content = response.get("choices", [])[0].get("message", {}).get("content", "⚠️ Resposta vazia")
            channel = self.env['mail.channel'].search([('name', 'ilike', 'OpenAi')], limit=1)
            if not channel:
                return {"error": "Canal 'OpenAi' não encontrado."}


            odoobot = self.env.ref('base.partner_root')
            author_id = odoobot.id if odoobot else self.env.user.partner_id.id

            msg_id = channel.message_post(
                body=content.replace("\n", "<br>"),  # evita quebras de linha no chat
                message_type='comment',
                subtype_xmlid='mail.mt_comment',
                author_id=author_id  # pode usar OdooBot se quiser
            ).id

            return {"id": msg_id}

        except Exception as e:
            return {"error": str(e), "raw_response": response}


    def _execute_simple(self, system_prompt, user_content, temperature=0):
        """
        Chamada direta sem campos de record — para classificação ou
        qualquer prompt sem contexto de modelo.
        Retorna o texto da resposta ou None em caso de erro.
        """
        self.ensure_one()
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_content},
            ],
            "temperature": temperature,
        }
        try:
            response = requests.post(
                self.ai_bridge_id.url,
                json=payload,
                auth=self._get_auth(),
                headers=self._get_headers(),
                timeout=30,
            )
            self.payload = payload
            response.raise_for_status()
            self.state = "done"
            self.result = response.content
            return response.json()["choices"][0]["message"]["content"]
        except Exception:
            self.state = "error"
            self.payload = payload
            buff = StringIO()
            traceback.print_exc(file=buff)
            self.error = buff.getvalue()
            buff.close()
            return None


    def _execute_agent(self, user_content, tools, execute_func_callback, system_prompt=None, history=None, max_iterations=10):        
        self.ensure_one()
        messages = [
            {"role": "system", "content": system_prompt or "Você é um assistente de negócios do Odoo."},
        ]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user_content})

        payload_tools = [{"type": "function", "function": f} for f in tools]

        for _ in range(max_iterations):
        
            payload = {
                "model": "gpt-4o-mini",
                "messages": messages,
                "tools": payload_tools,
                "tool_choice": "auto",
                "temperature": 0,
            }
            try:
                response = requests.post(
                    self.ai_bridge_id.url,
                    json=payload,
                    auth=self._get_auth(),
                    headers=self._get_headers(),
                    timeout=30,
                )
                response.raise_for_status()
                msg = response.json()["choices"][0]["message"]
                messages.append(msg)

                # Sem tool_calls → resposta final
                if not msg.get("tool_calls"):
                    self.state = "done"
                    self.result = response.content
                    return msg.get("content", "")

                # Executa todas as tools da rodada
               
                for tool_call in msg["tool_calls"]:
                    func_name = tool_call["function"]["name"]
                    func_args = json.loads(tool_call["function"]["arguments"])
                    result = execute_func_callback(func_name, func_args)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": json.dumps(result, ensure_ascii=False, default=str),
                    })

            except Exception:
                self.state = "error"
                buff = StringIO()
                traceback.print_exc(file=buff)
                self.error = buff.getvalue()
                buff.close()
                return "Desculpe, ocorreu um erro ao processar sua consulta."

        return "Não foi possível completar a consulta no número máximo de iterações."
