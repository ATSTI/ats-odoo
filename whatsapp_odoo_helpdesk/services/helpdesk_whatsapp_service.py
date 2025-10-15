from odoo import models, fields, api


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
            "1": {"team": "Suporte", "msg": "🔧 Seu chamado foi direcionado para o time de Suporte Técnico!"},
            "2": {"team": "Financeiro", "msg": "💰 Seu chamado foi enviado ao setor Financeiro."},
            "3": {"team": "Comercial", "msg": "🛒 Seu pedido foi encaminhado para o time Comercial."},
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
        if team:
            ticket.write({"team_id": team.id, "x_waiting_menu_response": False})           
            followers = team.user_ids
            if followers:
                ticket.message_subscribe(partner_ids=followers.mapped("partner_id").ids)
                for user in followers:
                    ticket.message_post(
                        body=f"📩 Novo chamado direcionado ao time {team.name} (de {partner.name}).",
                        message_type="comment",
                        subtype_xmlid="mail.mt_note",
                        author_id=user.partner_id.id,
                    )

            if instance:
                instance.send_text(phone_number, selected["msg"], partner=partner)
