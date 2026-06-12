# models/mail_message.py
import json
from datetime import datetime, timedelta
from odoo import models, api, fields
from odoo.fields import Datetime

QUERY_FUNCTIONS = [
    {
        "name": "get_sales_total",
        "description": "Retorna o total de vendas em um período de dias",
        "parameters": {
            "type": "object",
            "properties": {
                "days": {"type": "integer", "description": "Número de dias para trás a partir de hoje"},
                "state": {
                    "type": "string",
                    "enum": ["sale", "done", "all"],
                    "description": "Estado do pedido"
                }
            },
            "required": ["days"]
        }
    },
    {
        "name": "get_sales_by_partner",
        "description": "Retorna o total comprado por um cliente específico em um período",
        "parameters": {
            "type": "object",
            "properties": {
                "partner_name": {"type": "string", "description": "Nome parcial do cliente"},
                "days": {"type": "integer", "description": "Número de dias para trás"}
            },
            "required": ["partner_name", "days"]
        }
    },
    {
        "name": "get_top_products",
        "description": "Lista os produtos mais vendidos em um período",
        "parameters": {
            "type": "object",
            "properties": {
                "days": {"type": "integer"},
                "limit": {"type": "integer", "description": "Quantos produtos retornar (padrão 5)"}
            },
            "required": ["days"]
        }
    },

    {
        "name": "get_top_sellers",
        "description": "Lista os vendedores mais que mais venderam em um período",
        "parameters": {
            "type": "object",
            "properties": {
                "days": {"type": "integer"},
                "limit": {"type": "integer", "description": "Quantos vendedores retornar (padrão 5)"}
            },
            "required": ["days"]
        }
    },

    {
    "name": "prepare_invoice",
    "description": "Valida cliente e produtos e prepara uma fatura para confirmação posterior. Retorna os dados da fatura preparada ou erros encontrados. Caso o usuário confirme, então a função 'create_invoice' deve ser chamada com os mesmos dados para criar a fatura de fato.",
    "parameters": {
        "type": "object",
        "properties": {
            "partner_name": {"type": "string"},
            "lines": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "product_name": {"type": "string"},
                        "qty": {"type": "number"}
                    },
                    "required": ["product_name", "qty"]
                }
            }
        },
        "required": ["partner_name", "lines"]
    }
    },

    {
    "name": "get_overdue_invoices",
    "description": "Retorna faturas vencidas e o total em aberto. Pode filtrar por cliente e por quantidade de dias para trás.",
    "parameters": {
        "type": "object",
        "properties": {
            "partner_name": {
                "type": "string",
                "description": "Nome do cliente (opcional)"
            },
            "days": {
                "type": "integer",
                "description": "Buscar apenas faturas vencidas nos últimos X dias"
            }
        }
    }
},

{
    "name": "create_invoice",
    "description": "Cria uma fatura para um cliente com os produtos, quantidades e preços informados.",
    "parameters": {
        "type": "object",
        "properties": {
            "partner_name": {
                "type": "string",
                "description": "Nome do cliente"
            },
            "lines": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "product_name": {
                            "type": "string",
                            "description": "Nome do produto"
                        },
                        "qty": {
                            "type": "number",
                            "description": "Quantidade"
                        },
                        "unit_price": {
                            "type": "number",
                            "description": "Preço unitário"
                        }
                    },
                    "required": [
                        "product_name",
                        "qty"
                    ]
                }
            }
        },
        "required": [
            "partner_name",
            "lines"
        ]
    }
}
]


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
            odoobot = self.env['res.partner'].search(
                [('name', 'ilike', 'odoobot'), ('active', '=', False)], limit=1
            )
            if msg.author_id == odoobot:
                continue

            user_content = str(msg.body).replace('<p>', '').replace('</p>', '').strip()
            category = self._classify_message(user_content)

            if category in ('consulta', 'fatura'):
                self._run_query_agent(user_content, openai_channel)

            elif category == 'outro':
                bridge = self.env['ai.bridge'].search([('name', 'ilike', 'OpenAI')], limit=1)
                if bridge:
                    bridge.execute_ai_bridge(bridge.model_id.model, [], user_content)

            else:
                bridge = self.env['ai.bridge'].search([('name', 'ilike', category)], limit=1)
                if bridge:
                    ids = self.env[bridge.model_id.model].search(eval(bridge.domain)).ids
                    bridge.execute_ai_bridge(bridge.model_id.model, ids, user_content)

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
            'model_id': bridge.sudo().env['ir.model']._get_id('sale.order'),
        })

        answer = execution._execute_agent(
            user_content=user_content,
            tools=QUERY_FUNCTIONS,
            execute_func_callback=lambda fn, args: self._execute_query_function(fn, args),
            system_prompt=(
                f"Você é um assistente de negócios integrado ao Odoo. "
                f"Use as funções disponíveis para buscar os dados necessários e "
                f"responda de forma clara e objetiva em português. "
                f"Hoje é {datetime.now().strftime('%d/%m/%Y')}."
            ),
        )
        import pudb;pudb.set_trace()
        if answer:
            self._post_bot_message(channel, answer)

    def _execute_query_function(self, func_name, args):
        """Executa a query no ORM do Odoo e retorna dict com os dados."""
        since = Datetime.now() - timedelta(days=args.get('days', 30))
        since_str = since.strftime('%Y-%m-%d %H:%M:%S')
        # import pudb;pudb.set_trace()

        if func_name == 'get_sales_total':
            state = args.get('state', 'sale')
            domain = [('date_order', '>=', since_str)]
            if state != 'all':
                domain.append(('state', '=', state))
            orders = self.env['sale.order'].search(domain)
            return {
                'total': sum(orders.mapped('amount_total')),
                'currency': orders[:1].currency_id.name if orders else 'BRL',
                'count': len(orders),
                'period_days': args.get('days', 30),
            }

        elif func_name == 'get_sales_by_partner':
            partner_name = args.get('partner_name', '')
            partner = self.env['res.partner'].search(
                [('name', 'ilike', partner_name)], limit=1
            )
            if not partner:
                return {'error': f"Cliente '{partner_name}' não encontrado"}
            orders = self.env['sale.order'].search([
                ('partner_id', 'child_of', partner.id),
                ('date_order', '>=', since_str),
                ('state', 'in', ['sale', 'done']),
            ])
            return {
                'partner': partner.name,
                'total': sum(orders.mapped('amount_total')),
                'count': len(orders),
                'period_days': args.get('days', 30),
            }

        elif func_name == 'get_top_products':
            limit = args.get('limit', 5)
            lines = self.env['sale.order.line'].search([
                ('order_id.date_order', '>=', since_str),
                ('order_id.state', 'in', ['sale', 'done']),
            ])
            totals = {}
            for line in lines:
                name = line.product_id.name
                totals[name] = totals.get(name, 0) + line.product_uom_qty
            top = sorted(totals.items(), key=lambda x: x[1], reverse=True)[:limit]
            return {'top_products': [{'product': p, 'qty': q} for p, q in top]}
        
        elif func_name == 'get_top_sellers':
            limit = args.get('limit', 5)

            lines = self.env['sale.order.line'].search([
                ('order_id.date_order', '>=', since_str),
                ('order_id.state', 'in', ['sale', 'done']),
            ])

            totals = {}

            for line in lines:
                seller = line.order_id.user_id.name or 'Sem vendedor'
                totals[seller] = totals.get(seller, 0) + line.price_subtotal

            top = sorted(
                totals.items(),
                key=lambda x: x[1],
                reverse=True
            )[:limit]

            return {
                'top_sellers': [
                    {
                        'seller': seller,
                        'amount': amount
                    }
                    for seller, amount in top
                ]
            }
        
        elif func_name == 'prepare_invoice':
            partner_name = args.get('partner_name')
            lines = args.get('lines', [])
            partner = self.env['res.partner'].search([
                ('name', 'ilike', partner_name)
            ], limit=1)
            if not partner:
                return {
                    'error': f"Cliente '{partner_name}' não encontrado"
                }
            invoice_lines = []
            for item in lines:
                product = self.env['product.product'].search([
                    ('name', 'ilike', item['product_name'])
                ], limit=1)

                if not product:
                    return {
                        'error': f"Produto '{item['product_name']}' não encontrado"
                    }

                qty = item.get('qty', 1)

                price_unit = item.get('unit_price')

                if price_unit is None:
                    price_unit = product.lst_price

                invoice_lines.append((0, 0, {
                    'product_id': product.id,
                    'quantity': qty,
                    'price_unit': price_unit,
                }))

            move = self.env['account.move'].create({
                'move_type': 'out_invoice',
                'partner_id': partner.id,
                'invoice_line_ids': invoice_lines,
            })

            return {
                'success': True,
                'invoice_id': move.id,
                'invoice_name': move.name,
                'partner': partner.name,
                'total': move.amount_total,
                'message': (
                    f"Fatura {move.name} criada com sucesso "
                    f"para o cliente {partner.name}. "
                    f"Valor total: R$ {move.amount_total:.2f}"
                )
            }


        elif func_name == 'get_overdue_invoices':
            domain = [
                ('move_type', '=', 'out_invoice'),
                ('payment_state', '!=', 'paid'),
                ('invoice_date_due', '<', datetime.now().strftime('%Y-%m-%d')),
            ]
            days = args.get('days')
            partner_name = args.get('partner_name')
            if days:
                limit_date = fields.Date.today() - timedelta(days=days)

                domain.append(
                    ('invoice_date_due', '>=', limit_date)
                )
            if partner_name:
                partner = self.env['res.partner'].search(
                    [('name', 'ilike', partner_name)], limit=1
                )
                if partner:
                    domain.append(('partner_id', 'child_of', partner.id))
            invoices = self.env['account.move'].search(domain)
            return {
                'count': len(invoices),
                'total_overdue': sum(invoices.mapped('amount_residual')),
                'invoices': [
                    {
                        'name': inv.name,
                        'partner': inv.partner_id.name,
                        'amount': inv.amount_residual,
                        'due_date': inv.invoice_date_due.strftime('%d/%m/%Y') if inv.invoice_date_due else None,
                    }
                    for inv in invoices[:10]
                ],
            }

        return {'error': f"Função '{func_name}' não reconhecida"}

    def _post_bot_message(self, channel, content):
        import pudb;pudb.set_trace()
        odoobot = self.env['res.partner'].search(
            [('name', 'ilike', 'odoobot'), ('active', '=', False)], limit=1
        )
        channel.message_post(
            body=content.replace('\n', '<br>'),
            message_type='comment',
            subtype_xmlid='mail.mt_comment',
            author_id=odoobot.id if odoobot else self.env.user.partner_id.id,
        )