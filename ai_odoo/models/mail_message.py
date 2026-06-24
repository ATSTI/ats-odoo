# models/mail_message.py
import json
import ast
from datetime import datetime, timedelta
from odoo import models, api, fields
from odoo.fields import Datetime

EXCLUDED_PREFIXES = ('message_', 'website_', 'activity_')

QUERY_FUNCTIONS = [
    {
        "name": "query_odoo",
        "description": "Executa consultas em modelos Odoo autorizados",
        "parameters": {
            "type": "object",
            "properties": {
                "model": {
                    "type": "string"
                },
                "operation": {
                    "type": "string",
                    "enum": [
                        "search_read",
                        "search_count",
                        "read_group"
                    ]
                },
                "domain": {
                    "type": "array"
                },
                "fields": {
                    "type": "array"
                },
                "groupby": {
                    "type": "array"
                },
                "limit": {
                    "type": "integer"
                },
                "order": {
                    "type": "string"
                }
            },
            "required": [
                "model",
                "operation"
            ]
        }
    },
    {
        "name": "get_model_fields",
        "description": "Retorna os campos disponíveis de um modelo Odoo",
        "parameters": {
            "type": "object",
            "properties": {
                "model": {
                    "type": "string",
                    "description": "Nome técnico do modelo"
                }
            },
            "required": ["model"]
        }
    },
]

MODEL_FIELDS_WHITELIST = {
    "sale.order": [
        "name", "partner_id", "date_order", "amount_total",
        "state", "user_id", "team_id", "invoice_status",
    ],
    "sale.order.line": [
        "order_id", "product_id", "product_uom_qty",
        "price_unit", "price_subtotal", "state",
    ],
    "account.move": [
        "name", "partner_id", "invoice_date", "amount_total",
        "state", "move_type", "payment_state", "invoice_date_due",
    ],
    "res.partner": [
        "name", "email", "phone", "city", "state_id",
        "customer_rank", "supplier_rank",
    ],
    "product.product": [
        "name", "list_price", "standard_price",
        "categ_id", "type", "active",
    ],
    "stock.picking": [
        "name", "partner_id", "date_done", "state",
        "picking_type_id", "origin",
    ],
    "crm.lead": [
        "name", "partner_id", "expected_revenue", "stage_id",
        "user_id", "date_deadline", "probability",
    ],
}

FIELD_DESCRIPTIONS = {
    "account.move": {
        "invoice_date": "data de emissão da fatura",
        "invoice_date_due": "data de vencimento da fatura — use para filtrar faturas vencidas ou a vencer",
        "payment_state": "estado do pagamento: not_paid, partial, paid, reversed",
        "move_type": "tipo: out_invoice=venda, in_invoice=compra, out_refund=devolução venda",
        "state": "estado: draft=rascunho, posted=confirmada, cancel=cancelada",
    },
    "sale.order": {
        "state": "estado: draft=orçamento, sale=pedido confirmado, done=concluído, cancel=cancelado",
        "invoice_status": "estado faturamento: upselling, invoiced, to invoice, nothing",
    },
    "crm.lead": {
        "probability": "probabilidade de fechamento em %",
        "stage_id": "etapa do funil de vendas",
    }
}


class MailMessage(models.Model):
    _inherit = "mail.message"

    @api.model_create_multi
    def create(self, values_list):
        messages = super().create(values_list)
        openai_channel = self.env['mail.channel'].search(
            [('name', 'ilike', 'OpenAi')], limit=1
        )
        if not openai_channel:
            return messages

        for msg in messages:
            if msg.model != 'mail.channel' or msg.res_id != openai_channel.id:
                continue
            # import pudb;pudb.set_trace()
            odoobot = self.env.ref('base.partner_root')
            if msg.author_id == odoobot:
                continue

            user_content = str(msg.body).replace('<p>', '').replace('</p>', '').strip()
            # category = self._classify_message(user_content)
            # if category == 'consulta':
            self._run_query_agent(user_content, openai_channel)
            # elif category == 'acao':
            #     self._run_action_agent(user_content, openai_channel)

        return messages

    def _classify_message(self, content):
        """Usa ai.bridge para classificar — sem requests direto."""
        bridge = self.env['ai.bridge'].search([], limit=1)
        if not bridge:
            return 'outro'

        system_prompt = (
            "Você é um classificador. Responda APENAS com uma dessas palavras: "
            "crm, fatura, consulta, outro.\n"
            "Use 'consulta' para perguntas sobre dados como vendas, faturamento, "
            "clientes, produtos, pedidos ou relatórios."
        )
        execution = self.env['ai.bridge.execution'].create({
            'ai_bridge_id': bridge.id,
            'model_id': bridge.sudo().model_id.id,
        })
        answer = execution._execute_simple(
            system_prompt=system_prompt,
            user_content=content,
            temperature=0,
        )
        if not answer:
            return 'outro'
        return answer.strip().lower().split()[0]  # pega só a primeira palavra

    def _run_query_agent(self, user_content, channel):
        """Delega toda a chamada com function calling para ai.bridge.execution."""
        bridge = self.env['ai.bridge'].search([('name', 'ilike', 'OpenAI')], limit=1)
        # import pudb;pudb.set_trace()
        if not bridge:
            return

        execution = self.env['ai.bridge.execution'].create({
            'ai_bridge_id': bridge.id,
            'model_id': bridge.sudo().model_id.id,
        })

        answer = execution._execute_agent(
            user_content=user_content,
            tools=QUERY_FUNCTIONS,
            execute_func_callback=lambda fn, args: self._execute_query_function(fn, args),
            system_prompt=(
                f"""
                Você é um assistente de negócios integrado ao Odoo.

                Você possui acesso apenas à ferramenta query_odoo.

                Antes de consultar um modelo,
                utilize get_model_fields para conhecer
                os campos disponíveis.

                Nunca invente nomes de campos.

                Sempre use limites razoáveis.

                Quando receber os resultados,
                resuma-os de forma objetiva em português.

                Caso não existam dados,
                informe isso claramente.
                Hoje é {datetime.now().strftime('%d/%m/%Y')}.
                """
            ),
            
        )

        if answer:
            self._post_bot_message(channel, answer)

    def _validate_domain(self, domain):
        if not isinstance(domain, list):
            return []
        allowed_operators = {'=', '!=', '>', '<', '>=', '<=', 'in', 'not in', 'like', 'ilike'}
        for item in domain:
            if isinstance(item, (str,)):  # '&', '|', '!'
                continue
            if not (isinstance(item, (list, tuple)) and len(item) == 3):
                return []
            field, op, _ = item
            if op not in allowed_operators:
                return []
            if '.' in str(field):  # bloqueia dot-notation
                return []
        return domain

    def _execute_query_function(self, func_name, args):

        allowed_models = {
            "sale.order",
            "sale.order.line",
            "account.move",
            "res.partner",
            "product.product",
            "stock.picking",
            "crm.lead",
        }

        if func_name == "get_model_fields":
            model_name = args.get("model")
            if model_name not in allowed_models:
                return {"error": f"Modelo {model_name} não permitido"}

            allowed_fields = MODEL_FIELDS_WHITELIST.get(model_name, [])
            model = self.env[model_name]
            descriptions = FIELD_DESCRIPTIONS.get(model_name, {})

            return {
                field_name: {
                    "type": model._fields[field_name].type,
                    "string": model._fields[field_name].string,
                    "description": descriptions.get(field_name, ""),
                }
                for field_name in allowed_fields
                if field_name in model._fields
            }
        
        elif func_name == "query_odoo":
            model_name = args.get("model")

            if model_name not in allowed_models:
                return {
                    "error": f"Modelo {model_name} não permitido"
                }

            model = self.env[model_name]

            operation = args["operation"]
            allowed_fields = set(MODEL_FIELDS_WHITELIST.get(model_name, []))
            requested = set(args.get("fields") or [])
            safe_fields = list(requested & allowed_fields) or list(allowed_fields)

            if operation == "search_read":
                try:
                    
                    return model.search_read(
                        domain=self._validate_domain(args.get("domain", [])),
                        fields=safe_fields,
                        limit=min(args.get("limit", 50), 100),
                        order=args.get("order")
                    )
                except Exception as e:
                    return {
                        "error": f"Erro na consulta (search_read): {str(e)}"
                    }

            elif operation == "search_count":
                try:
                    return {
                        "count": model.search_count(
                            self._validate_domain(args.get("domain", []))
                        )
                    }
                except Exception as e:
                    return {
                        "error": f"Erro na contagem (search_count): {str(e)}"
                    }

            elif operation == "read_group":
                try:
                    return model.read_group(
                        domain=self._validate_domain(args.get("domain", [])),
                        fields=safe_fields,
                        groupby=args.get("groupby", []),
                        limit=args.get("limit", 50),
                        lazy=False
                    )
                except Exception as e:
                    return {
                        "error": f"Erro na consulta agrupada (read_group): {str(e)}"
                    }

            return {
                "error": "Operação inválida"
            }
        else:
            return {
                "error": "Função não permitida"
            }

    def _post_bot_message(self, channel, content):
        odoobot = self.env.ref('base.partner_root')
        channel.message_post(
            body=content.replace('\n', '<br>'),
            message_type='comment',
            subtype_xmlid='mail.mt_comment',
            author_id=odoobot.id if odoobot else self.env.user.partner_id.id,
        )