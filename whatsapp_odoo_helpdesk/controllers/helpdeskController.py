# -*- coding: utf-8 -*-
import logging
from odoo import http
from odoo.http import request
from odoo.addons.whatsapp_contact_management.controllers.main import ContactWebhookController

_logger = logging.getLogger(__name__)


class HelpdeskWhatsappWebhookController(ContactWebhookController):

    @http.route('/whatsapp/webhook', type='json', auth='public', methods=['POST'], csrf=False)
    def receive_webhook(self, **kwargs):
        try:
            payload = request.get_json_data() or {}

            event = payload.get('event')
            message_data = payload.get('data', {}) or {}

            is_message_event = (
                event in (None, 'messages.upsert', 'messages.update', 'messages')
                or message_data.get('message')
            )

            if not is_message_event:
                return super().receive_webhook()


            message_data = payload.get('data', {}) or {}
            key = message_data.get('key', {}) or {}
            message_content = message_data.get('message', {}) or {}

            if key.get('fromMe'):
                return super().receive_webhook()

            message_id = key.get('id')
            if message_id and request.env['whatsapp.message'].sudo().search_count([('message_id', '=', message_id)]):
                _logger.info("Mensagem duplicada detectada (id=%s)", message_id)
                return super().receive_webhook()

            sender_jid = key.get('remoteJid') or ''
            phone_number = sender_jid.split('@')[0] if sender_jid else None
            if not phone_number:
                _logger.warning("Nenhum número de telefone no payload.")
                return super().receive_webhook()

            partner = request.env['res.partner'].sudo().search([('mobile', 'ilike', phone_number)], limit=1)
            if not partner:
                _logger.info("Parceiro não encontrado para o número %s", phone_number)
                return super().receive_webhook()

            Ticket = request.env['helpdesk.ticket'].sudo()
            ticket = Ticket.search([
                ('partner_id', '=', partner.id),
                ('stage_id.fold', '=', False)
            ], order='id desc', limit=1)

            if not ticket:
                Stage = request.env['helpdesk.ticket.stage'].sudo()
                stage_new = Stage.search([('name', 'ilike', 'novo')], limit=1)
                if not stage_new:
                    _logger.error("Stage 'Novo' não encontrado.")
                    return super().receive_webhook()

                ticket_vals = {
                    'name': f'WhatsApp: {partner.name or phone_number}',
                    'partner_id': partner.id,
                    'partner_name': partner.name,
                    'stage_id': stage_new.id,
                    'tag_ids': [(6, 0, partner.category_id.ids)],
                    'description': "Ticket criado via WhatsApp",
                    'x_waiting_menu_response': True,
                    'email_cc':None,
                }
                if 'x_waiting_department' in Ticket._fields:
                    ticket_vals['x_waiting_department'] = True
                if 'x_whatsapp_number' in Ticket._fields:
                    ticket_vals['x_whatsapp_number'] = phone_number

                ticket = Ticket.with_context(skip_whatsapp_auto=True).create(ticket_vals)
                _logger.info("Novo ticket #%s criado para %s", ticket.id, partner.name)
                instance = request.env['whatsapp.instance'].sudo().search([('status', '=', 'connected')], limit=1)
                if instance:
                    try:
                        instance.send_text(
                            phone_number,
                            "Olá! 👋 Para direcionar seu atendimento, escolha uma opção:\n1️⃣ Suporte\n2️⃣ Financeiro\n3️⃣ Comercial",
                            partner=partner
                        )
                    except Exception as ex:
                        _logger.exception("Erro ao enviar menu inicial: %s", ex)

                return {'status': 'ok', 'message': 'Ticket criado e menu enviado'}
            try:
                body, attachment_ids = self._extract_message_content_and_attachments(message_content)
            except Exception as ex:
                _logger.exception("Falha ao extrair mídia: %s", ex)
                body = (
                    message_content.get('conversation')
                    or message_content.get('extendedTextMessage', {}).get('text', '')
                    or ''
                )
                attachment_ids = []
            if getattr(ticket, 'x_waiting_menu_response', False):
                try:
                    service = request.env["helpdesk.whatsapp.service"].sudo()
                    service.process_incoming_message(ticket, partner, body or '', phone_number)
                except Exception as ex_service:
                    _logger.exception("Erro ao processar resposta do menu no ticket #%s: %s", ticket.id, ex_service)
                return {'status': 'ok', 'message': 'Menu response processed'}

            if (body and body.strip()) or attachment_ids:
                try:
                    message = ticket.with_context(skip_whatsapp_send=True).sudo().message_post(
                        body=body,
                        message_type='comment',
                        subtype_xmlid='mail.mt_comment',
                        author_id=partner.id,
                        attachment_ids=attachment_ids if attachment_ids else None
                    )
                    ticket.with_context(force_send_bus=True).trigger_ticket_refresh()
                    _logger.info("Mensagem postada no ticket #%s: %s", ticket.id, body)

                    if ticket.user_id and ticket.user_id.partner_id:
                        ticket.user_id.partner_id._bus_send(
                            "web_notify",
                            {
                                "type": "info",
                                "title": "Nova mensagem no ticket que voce se atribuiu",
                                "message": f"Ticket #{ticket.name}: nova mensagem de {partner.name}",
                                "model": "helpdesk.ticket",
                                "params": {"ticket_id": ticket.id},
                            },
                        )
                        _logger.info("Notificação enviada via bus.bus para %s", ticket.user_id.name)


                except Exception as ex_post:
                    _logger.exception("Erro ao postar mensagem no ticket #%s: %s", ticket.id, ex_post)

            try:
                result = super().receive_webhook()
            except Exception as ex_super:
                _logger.exception("Erro ao chamar super(): %s", ex_super)
                return {'status': 'ok', 'message': 'Processed locally; super() failed'}

            return result or {'status': 'ok', 'message': 'Message processed'}

        except Exception as e:
            _logger.error("Falha geral no webhook Helpdesk: %s", e, exc_info=True)
            return {'status': 'error', 'message': str(e)}
