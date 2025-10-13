# -*- coding: utf-8 -*-
import logging
from odoo import http
from odoo.http import request
from odoo.addons.whatsapp_evolution_base.controllers.webhook_controller import WhatsappWebhookController as OriginalWebhook

_logger = logging.getLogger(__name__)

class HelpdeskWhatsappWebhookController(OriginalWebhook):
    @http.route('/whatsapp/webhook', type='json', auth='public', methods=['POST'], csrf=False)
    def receive_webhook(self, **kwargs):
        """
        Intercepta mensagens inbound do WhatsApp para helpdesk:
        - Evita mensagens duplicadas
        - Ignora "Chamado Criado"
        - Cria ticket se não existir
        - Posta mensagem no chatter sem reenvio para WhatsApp
        """
        try:
            payload = request.get_json_data() or {}
            event = payload.get('event')
            if event != 'messages.upsert':
                return {'status': 'ok', 'message': 'Ignored non-message event'}

            message_data = payload.get('data', {})
            key = message_data.get('key', {})
            message_content = message_data.get('message', {})

           
            if key.get('fromMe'):
                return {'status': 'ok', 'message': 'Message from bot ignored'}

            message_id = key.get('id')
            if request.env['whatsapp.message'].sudo().search_count([('message_id', '=', message_id)]):
                _logger.info("Mensagem duplicada ignorada: %s", message_id)
                return {'status': 'ok', 'message': 'Duplicate message ignored'}

            
            body = message_content.get('conversation') or \
                   message_content.get('extendedTextMessage', {}).get('text', '')

            if body and "Chamado Criado" in body:
                _logger.info("Mensagem automática 'Chamado Criado' ignorada.")
                return {'status': 'ok', 'message': 'Automated message ignored'}

            sender_jid = key.get('remoteJid')
            phone_number = sender_jid.split('@')[0]

            partner = request.env['res.partner'].sudo().search([('mobile', 'ilike', phone_number)], limit=1)
            if not partner:
                return {'status': 'ok', 'message': 'Partner not found'}

          
            ticket = request.env['helpdesk.ticket'].sudo().search([
                ('partner_id', '=', partner.id),
                ('stage_id.fold', '=', False)
            ], order='id desc', limit=1)

            if not ticket:
                stage_new = request.env['helpdesk.ticket.stage'].sudo().search([('name', 'ilike', 'novo')], limit=1)
                if not stage_new:
                    _logger.error("Stage 'NOVO' não encontrado!")
                    return {'status': 'ok', 'message': 'Stage NOVO not found'}

                ticket_vals = {
                    'name': f'WhatsApp: {partner.name}',
                    'partner_id': partner.id,
                    'stage_id': stage_new.id,
                    'description': "Ticket criado via WhatsApp",
                }

                HelpdeskTicket = request.env['helpdesk.ticket'].sudo()
                if 'x_waiting_department' in HelpdeskTicket._fields:
                    ticket_vals['x_waiting_department'] = True
                if 'x_whatsapp_number' in HelpdeskTicket._fields:
                    ticket_vals['x_whatsapp_number'] = phone_number

                ticket = HelpdeskTicket.create(ticket_vals)
                _logger.info("Novo ticket #%s criado para partner %s.", ticket.id, partner.name)

                instance = request.env['whatsapp.instance'].sudo().search([('status', '=', 'connected')], limit=1)
                if instance:
                    instance.send_text(
                        phone_number,
                        "Olá! Para direcionar seu atendimento, escolha uma opção:\n1️⃣ Suporte\n2️⃣ Financeiro\n3️⃣ Comercial",
                        partner=partner
                    )

        
            if body:
                whatsapp_user = request.env['res.users'].sudo().search([('login', '=', 'whatsapp_bot')], limit=1)
                if not whatsapp_user:
                    whatsapp_user = request.env['res.users'].sudo().create({
                        'name': 'WhatsApp Bot',
                        'login': 'whatsapp_bot',
                        'email': 'whatsapp-bot@example.com',
                    })

          
                ticket.message_post(
                    body=f"<b>{partner.name}:</b> {body}",
                    message_type='comment',
                    subtype_xmlid='mail.mt_comment',
                    author_id=whatsapp_user.partner_id.id,
                    context={'from_webhook': True},
                )
                _logger.info("Mensagem do partner '%s' postada no ticket #%s.", partner.name, ticket.id)

            return {'status': 'ok', 'message': 'Message processed'}

        except Exception as e:
            _logger.error("Falha ao processar webhook do Helpdesk: %s", e, exc_info=True)
            return {'status': 'error', 'message': str(e)}
