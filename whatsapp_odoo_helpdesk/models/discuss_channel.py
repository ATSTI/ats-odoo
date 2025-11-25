from odoo import models, fields, Command
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class DiscussChannel(models.Model):
    _inherit = "discuss.channel"

    def _add_members_to_whatsapp_channel(self, channel, partner, instance):
        """Adiciona membros internos da equipe 'Suporte' + o cliente (partner)
        ao canal do WhatsApp, evitando duplicados e validando membros existentes.
        """
        suporte_team = self.env['helpdesk.ticket.team'].search(
            [('name', 'ilike', 'suporte')], limit=1
        )
        suporte_members = set()

        if suporte_team:
            if hasattr(suporte_team, "member_ids") and suporte_team.member_ids:
                suporte_members = set(suporte_team.member_ids.mapped("partner_id"))
            elif hasattr(suporte_team, "user_ids") and suporte_team.user_ids:
                suporte_members = set(suporte_team.user_ids.mapped("partner_id"))

        all_internal_user_partners = set(
            self.env['res.users'].search([]).mapped('partner_id')
        )
        valid_internal_members = suporte_members.intersection(all_internal_user_partners)
        members_to_add = valid_internal_members | {partner}
        existing_member_ids = set(channel.channel_member_ids.mapped('partner_id').ids)
        new_partners = [p for p in members_to_add if p.id not in existing_member_ids]
        if not new_partners:
            return  
        commands = []
        for p in new_partners:
            commands.append(
                Command.create({
                    "partner_id": p.id,
                    "is_pinned": (p.id != partner.id),
                })
            )

        channel.write({"channel_member_ids": commands})

        _logger.info(
            "Adicionados ao canal %s: %s",
            channel.id,
            ", ".join([str(p.id) for p in new_partners])
        )
