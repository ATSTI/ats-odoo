from odoo import models, api
from odoo.tools import html2plaintext
import logging

_logger = logging.getLogger(__name__)

class HelpDeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    def message_post(self, **kwargs):
        """
        Intercepta mensagens do chatter do ticket e envia para WhatsApp
        usando whatsapp.evolution.composer, evitando duplicações e loops.
        """
        messages = super(HelpDeskTicket, self).message_post(**kwargs)

        for message in messages:
           
            if self.env.context.get('from_webhook') or self.env.context.get('from_composer'):
                continue

            ticket = self.browse(message.res_id)
            partner = ticket.partner_id
            if not partner or not partner.mobile:
                continue

            try:
                body = html2plaintext(message.body or "")
                attachments = message.attachment_ids

                if not body and not attachments:
                    continue

              
                if body and "Chamado criado" in body: #nao ta funfando, n sei pq fica enviando esse Chamado criado
                    _logger.info(
                        "Mensagem automática 'Chamado Criado' ignorada no ticket #%s.", ticket.id
                    )
                    continue

           
                composer_vals = {
                    'partner_id': [(6, 0, [partner.id])],
                    'body': body,
                    'attachment_ids': [(6, 0, attachments.ids)],
                    'instance_id': self.env['whatsapp.instance'].sudo().search(
                        [('status', '=', 'connected')], limit=1
                    ).id,
                    'model': 'helpdesk.ticket',
                    'res_id': ticket.id,
                }

             
                composer = self.env['whatsapp.evolution.composer'].with_context(from_composer=True).sudo().create(composer_vals)
                composer.sudo().action_send_message()

                _logger.info(
                    "Mensagem do ticket #%s enviada para WhatsApp do partner '%s' via Composer.",
                    ticket.id, partner.name
                )

            except Exception as e:
                _logger.error(
                    "Falha ao enviar mensagem do ticket #%s para WhatsApp: %s",
                    ticket.id, e, exc_info=True
                )

        return messages

    