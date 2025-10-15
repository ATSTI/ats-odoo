from odoo import models, api, fields
from odoo.tools import html2plaintext
import logging
from datetime import timedelta, datetime

_logger = logging.getLogger(__name__)

class HelpDeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    x_waiting_menu_response = fields.Boolean(
        string="Aguardando resposta do menu",
        default=False,
        help="Indica se o ticket está aguardando resposta do menu enviado via WhatsApp"
    )

    def message_post(self, **kwargs):
        """
        Intercepta mensagens do chatter do ticket e envia para WhatsApp
        usando whatsapp.evolution.composer, evitando duplicações e loops.
        """
        messages = super(HelpDeskTicket, self).message_post(**kwargs)

        for message in messages:          
            if self.env.context.get('skip_whatsapp_send') or self.env.context.get('from_composer'):
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
                if body and "Chamado criado" in body: 
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
    


    def action_close_ticket(self):
        """
        Botão: Encerrar ticket
        - Finaliza o ticket (muda estágio para 'Concluído')
        - Envia mensagem automática via WhatsApp com protocolo
        """
        self.ensure_one()

        # Buscar parceiro
        partner = self.partner_id
        if not partner or not partner.mobile:
            _logger.warning("Ticket #%s não possui partner ou número de WhatsApp.", self.id)
            return

      
        stage_closed = self.env['helpdesk.ticket.stage'].sudo().search(
            [('name', 'ilike', 'concluído')], limit=1
        )
        if stage_closed:
            self.write({'stage_id': stage_closed.id, 'closed': True}) 
        else:
            _logger.warning("Não foi possível encontrar stage 'Concluído' para ticket #%s.", self.id)

      
        now = datetime.now()
        protocolo = f"{now.year:04d}{now.month:02d}{now.day:02d}{self.id}"

    
        body = (
            f"👋 Olá {partner.name}, tudo bem?\n\n"
            "Seu chamado foi finalizado com sucesso. "
            "Esta é uma mensagem automática, não é necessário responder.\n\n"
            f"📄 Protocolo de Atendimento: {protocolo}\n"
            "Agradecemos seu contato! 🙏"
        )

       
        try:
            instance = self.env["whatsapp.instance"].sudo().search(
                [("status", "=", "connected")], limit=1
            )
            if instance:
                composer_vals = {
                    "partner_id": [(6, 0, [partner.id])],
                    "body": body,
                    "instance_id": instance.id,
                    "model": "helpdesk.ticket",
                    "res_id": self.id,
                }
                composer = self.env["whatsapp.evolution.composer"].with_context(
                    from_composer=True
                ).sudo().create(composer_vals)
                composer.sudo().action_send_message()
                _logger.info("Mensagem WhatsApp enviada ao partner %s do ticket #%s", partner.name, self.id)

        except Exception as e:
            _logger.error("Erro ao enviar mensagem WhatsApp no fechamento do ticket #%s: %s", self.id, e, exc_info=True)
    
    def assign_to_me(self):
        """
        Quando o usuário clica em 'Atribuir a mim', atribui o ticket e envia:
        - Mensagem ao cliente via WhatsApp
        - Notificação interna via OdooBot no Discuss
        """
        self.write({"user_id": self.env.user.id})
        user = self.env.user

        for ticket in self:
            partner = ticket.partner_id
            if not partner or not partner.mobile:
                continue

            try:
             
                body = (
                    f"👋 Olá {partner.name}, tudo bem?\n\n"
                    f"Seu chamado foi atribuído a {user.name}.\n"
                    "Em breve entraremos em contato para ajudar você! 💬"
                )

                instance = self.env["whatsapp.instance"].sudo().search(
                    [("status", "=", "connected")], limit=1
                )
                if instance:
                    composer_vals = {
                        "partner_id": [(6, 0, [partner.id])],
                        "body": body,
                        "instance_id": instance.id,
                        "model": "helpdesk.ticket",
                        "res_id": ticket.id,
                    }
                    composer = (
                        self.env["whatsapp.evolution.composer"]
                        .with_context(from_composer=True)
                        .sudo()
                        .create(composer_vals)
                    )
                    composer.sudo().action_send_message()

                odoo_bot = self.env.ref("base.partner_root")  
                Channel = self.env["discuss.channel"].sudo()
                followers = ticket.team_id.user_ids
                for team_user in followers:
                    if team_user == user:
                        continue  
                    user_partner = team_user.partner_id
                    chat = Channel.search([
                        ("channel_type", "=", "chat"),
                        ("channel_partner_ids", "in", [odoo_bot.id]),
                        ("channel_partner_ids", "in", [user_partner.id]),
                    ], limit=1)                
                    if not chat:
                        chat = Channel.create({
                            "channel_type": "chat",
                            "name": f"Chat OdooBot - {team_user.name}",
                            "channel_partner_ids": [(6, 0, [odoo_bot.id, user_partner.id])],
                        })               
                    chat.message_post(
                        body=(
                            f"👤 {user.name} atribuiu o chamado "
                            f"ID do ticket: {ticket.id}/// Nome do Ticket: {ticket.name}"
                            f"a si mesmo.\n"
                            f"🧩 Time: {ticket.team_id.name}"
                        ),
                        message_type="comment",
                        subtype_xmlid="mail.mt_comment",
                        author_id=odoo_bot.id,
                    )
                _logger.info(
                    "Mensagem WhatsApp e notificação interna enviadas para o ticket #%s.",
                    ticket.id,
                )
            except Exception as e:
                _logger.error(
                    "Erro ao processar atribuição e notificações do ticket %s: %s",
                    ticket.id,
                    e,
                    exc_info=True,
                )


    