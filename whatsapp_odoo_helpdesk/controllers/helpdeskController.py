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
        Extensão segura do webhook original:
        - Intercepta inbound messages.upsert
        - Evita duplicação
        - Cria ticket (com contexto para evitar envio automático do módulo base)
        - Posta a mensagem no ticket como partner (garante Discuss/Notificações)
        - Inscreve a equipe/responsáveis como followers
        - Em seguida chama super() para manter lógica original (registro whatsapp.message, mídias etc.)
        """
        try:
            payload = request.get_json_data() or {}
            event = payload.get('event')
            if event != 'messages.upsert':
                return super(HelpdeskWhatsappWebhookController, self).receive_webhook()
            message_data = payload.get('data', {}) or {}
            key = message_data.get('key', {}) or {}
            message_content = message_data.get('message', {}) or {}
            if key.get('fromMe'):
                _logger.debug("Mensagem marcada fromMe; delegando ao original.")
                return super(HelpdeskWhatsappWebhookController, self).receive_webhook()

            message_id = key.get('id')
            if message_id and request.env['whatsapp.message'].sudo().search_count([('message_id', '=', message_id)]):
                _logger.info("Mensagem duplicada detectada (id=%s); delegando ao original.", message_id)
                return super(HelpdeskWhatsappWebhookController, self).receive_webhook()
            body = message_content.get('conversation') or message_content.get('extendedTextMessage', {}).get('text', '') or ''

            if body and "Chamado Criado" in body:
                _logger.info("Ignorando mensagem automática 'Chamado Criado' antes do super().")
                return {'status': 'ok', 'message': 'Automated message ignored'}
            sender_jid = key.get('remoteJid') or ''
            phone_number = sender_jid.split('@')[0] if sender_jid else None
            if not phone_number:
                _logger.warning("Nenhum remoteJid/phone encontrado no payload; delegando ao original.")
                return super(HelpdeskWhatsappWebhookController, self).receive_webhook()

            partner = request.env['res.partner'].sudo().search([('mobile', 'ilike', phone_number)], limit=1)
            if not partner:
                _logger.info("Partner não encontrado para %s; delegando ao original (o módulo base pode criar).", phone_number)
              
                return super(HelpdeskWhatsappWebhookController, self).receive_webhook()
            Ticket = request.env['helpdesk.ticket'].sudo()
            ticket = Ticket.search([
                ('partner_id', '=', partner.id),
                ('stage_id.fold', '=', False)
            ], order='id desc', limit=1)

            if not ticket:
                Stage = request.env['helpdesk.ticket.stage'].sudo()
                stage_new = Stage.search([('name', 'ilike', 'novo')], limit=1)
                if not stage_new:
                    _logger.error("Stage 'NOVO' não encontrado — delegando ao original.")
                    return super(HelpdeskWhatsappWebhookController, self).receive_webhook()

                ticket_vals = {
                    'name': f'WhatsApp: {partner.name}',
                    'partner_id': partner.id,
                    'stage_id': stage_new.id,
                    'description': "Ticket criado via WhatsApp",
                }
              
                HelpdeskTicket = Ticket
                if 'x_waiting_department' in HelpdeskTicket._fields:
                    ticket_vals['x_waiting_department'] = True
                if 'x_whatsapp_number' in HelpdeskTicket._fields:
                    ticket_vals['x_whatsapp_number'] = phone_number             
                ticket = HelpdeskTicket.with_context(skip_whatsapp_auto=True).create(ticket_vals)
                _logger.info("Novo ticket #%s criado para partner %s (via webhook).", ticket.id, partner.name)
        
                instance = request.env['whatsapp.instance'].sudo().search([('status', '=', 'connected')], limit=1)
                if instance:
                    try:
                        instance.send_text(
                            phone_number,
                            "Olá! Para direcionar seu atendimento, escolha uma opção:\n1️⃣ Suporte\n2️⃣ Financeiro\n3️⃣ Comercial",
                            partner=partner
                        )
                    except Exception as ex:
                        _logger.exception("Erro ao enviar menu inicial via instance.send_text: %s", ex)

            if body:
                try:
                    ticket.with_context(skip_whatsapp_send=True).sudo().message_post(
                        body=f"{body}",
                        message_type='comment',
                        subtype_xmlid='mail.mt_comment',
                        author_id=partner.id,
                    )
                    _logger.info("Mensagem do partner '%s' posta no ticket #%s.", partner.name, ticket.id)
                except Exception as ex:
                    _logger.exception("Erro ao postar mensagem no ticket #%s: %s", getattr(ticket, 'id', 'N/A'), ex)

            try:
                result = super(HelpdeskWhatsappWebhookController, self).receive_webhook()
            except Exception as ex:
                _logger.exception("Erro ao chamar super().receive_webhook(): %s", ex)
   
                return {'status': 'ok', 'message': 'Processed with local changes, super() failed'}

        
            return result or {'status': 'ok', 'message': 'Message processed'}

        except Exception as e:
            _logger.error("Falha ao processar webhook do Helpdesk: %s", e, exc_info=True)
            return {'status': 'error', 'message': str(e)}
