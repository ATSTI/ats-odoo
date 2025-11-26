from odoo import models, fields, Command,_ as odoo_t, Command
from odoo.exceptions import UserError
from odoo.tools import html2plaintext
import logging

_logger = logging.getLogger(__name__)

class DiscussChannel(models.Model):
    _inherit = "discuss.channel"

    def _add_members_to_whatsapp_channel(self, channel, partner, instance):
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

    def _notify_thread(self, message, msg_vals=False, **kwargs):
        msg_vals = msg_vals or {}

        original_body = html2plaintext(msg_vals.get("body", ""))
        author = message.author_id.name or "Equipe"
        formatted_body = f"*{author}:*\n{original_body}"
        msg_vals["body"] = formatted_body
        customer_partner = next(
            (p for p in self.channel_partner_ids if not p.user_ids),
            None
        )
        partner_id = customer_partner.id if customer_partner else None

        ticket = None
        if partner_id:
            ticket = self.env['helpdesk.ticket'].sudo().search([
                ('partner_id', '=', partner_id),
                ('stage_id.closed', '=', False),
            ], limit=1)
        if (
            partner_id
            and ticket
            and not self.env.context.get("skip_whatsapp_send")
            and not self.env.context.get("from_webhook")
        ):
            ticket.with_context(skip_whatsapp_send=True).sudo().message_post(
                body=formatted_body,
                message_type="comment",
                subtype_xmlid="mail.mt_comment",
            )

        return super()._notify_thread(message, msg_vals, **kwargs)



