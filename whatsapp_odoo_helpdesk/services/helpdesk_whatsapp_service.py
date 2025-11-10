from odoo import models, api

class HelpdeskWhatsappService(models.AbstractModel):
    _name = "helpdesk.whatsapp.service"
    _description = "Serviço de processamento de mensagens WhatsApp do Helpdesk"

    def process_incoming_message(self, ticket, partner, body, phone_number):
        """
        Processa respostas do menu do WhatsApp.
        """

        if not ticket or not partner:
            return
        menu_options = {
            "1": {"team": "Suporte", "msg": "🔧 Seu chamado foi direcionado para o time de Suporte Técnico! Como podemos ajudá-lo?"},
            "2": {"team": "Financeiro", "msg": "💰 Seu chamado foi enviado ao setor Financeiro! Como podemos ajudá-lo?"},
            "3": {"team": "Comercial", "msg": "🛒 Seu pedido foi encaminhado para o time Comercial! Como podemos ajudá-lo?"},
        }
        choice = body.strip()
        selected = menu_options.get(choice)
        instance = self.env["whatsapp.instance"].sudo().search([("status", "=", "connected")], limit=1)
        if not selected:
            if instance:
                instance.send_text(phone_number, "Opção inválida. Escolha 1️⃣, 2️⃣ ou 3️⃣.", partner=partner)
            return
        team_name = selected["team"]
        Team = self.env["helpdesk.ticket.team"].sudo()
        team = Team.search([("name", "ilike", team_name)], limit=1)
        if not team:
            return

        ticket.write({"team_id": team.id, "x_waiting_menu_response": False})
        followers = team.user_ids
        if not followers:
            return

        ticket.message_subscribe(partner_ids=followers.mapped("partner_id").ids)
        odoo_bot = self.env.ref("base.partner_root")
        Channel = self.env["discuss.channel"].sudo()
        for user in followers:
            user_partner = user.partner_id
            chat = Channel.search([
                ("channel_type", "=", "chat"),
                ("channel_partner_ids", "in", [odoo_bot.id]),
                ("channel_partner_ids", "in", [user_partner.id]),
            ], limit=1)
            if not chat:
                chat = Channel.create({
                    "channel_type": "chat",
                    "name": f"Chat OdooBot - {user.name}",
                })
                chat.channel_partner_ids = [(4, odoo_bot.id), (4, user_partner.id)]
            if chat:
                chat.ensure_one()
                chat.message_post(
                    body=f"📩 Novo chamado direcionado ao time {team.name} (de {partner.name})\n"
                        f"🎟️ Ticket: ID {ticket.id} — {ticket.name}",
                    message_type="comment",
                    subtype_xmlid="mail.mt_comment",
                    author_id=odoo_bot.id,
                )
        if instance:
            instance.send_text(phone_number, selected["msg"], partner=partner)
