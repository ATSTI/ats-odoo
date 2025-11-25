from odoo import models, fields,Command
from odoo.exceptions import UserError
from odoo.tools import html2plaintext
import logging
_logger = logging.getLogger(__name__)

class DiscussChannel(models.Model):
    _inherit = "discuss.channel"


    def _add_members_to_whatsapp_channel(self, channel, partner, instance):
        """
        Adiciona os membros corretos ao canal e o afixa para novos membros.
        """
        members_to_add = {partner}
        if instance.user_id:
            members_to_add.add(instance.user_id.partner_id)
         
        if instance.instance_type == 'company' and not instance.user_id:
            admin_group = self.env.ref('base.group_users', raise_if_not_found=False)
            if admin_group:
                admin_users = self.env['res.users'].search([('groups_id', 'in', admin_group.id)])
                for user in admin_users:
                    members_to_add.add(user.partner_id)

        current_member_ids = channel.channel_member_ids.mapped('partner_id').ids
        # Filtra apenas os parceiros que ainda não são membros do canal.
        new_partners = [p for p in members_to_add if p.id not in current_member_ids]

        if new_partners:
            commands = []
            for p in new_partners:
                # Para usuários internos, afixa o canal na criação. O contato externo não precisa disso.
                is_internal = p.id != partner.id
                commands.append(Command.create({'partner_id': p.id, 'is_pinned': is_internal}))
            
            channel.write({
                'channel_member_ids': commands
            })
