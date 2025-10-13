# # -*- coding: utf-8 -*-
# from odoo import api, fields, models, _ as odoo_t, Command
# from odoo.tools import html2plaintext
# from odoo.exceptions import UserError
# import logging

# _logger = logging.getLogger(__name__)

# class DiscussChannel(models.Model):
#     _inherit = 'discuss.channel'

#     channel_type = fields.Selection(
#         selection_add=[('whatsapp', 'WhatsApp Conversation')],
#         ondelete={'whatsapp': 'cascade'})
    
#     whatsapp_instance_id = fields.Many2one('whatsapp.instance', string="WhatsApp Instance", readonly=True)
#     whatsapp_partner_id = fields.Many2one('res.partner', string="WhatsApp Partner", readonly=True)


#     @api.model
#     def get_or_create_whatsapp_channel_for_partner(self, partner_id):
#         """
#         Método chamado pelo frontend para iniciar uma conversa.
#         """
#         partner = self.env['res.partner'].browse(partner_id)
#         if not partner.phone:
#             raise UserError(_("O contato selecionado não possui um número de celular."))
#         instance = self.env['whatsapp.instance'].search([('status', '=', 'connected')], limit=1)
#         if not instance:
#             raise UserError(_("Nenhuma instância do WhatsApp conectada e disponível foi encontrada."))
#         channel = self._find_or_create_whatsapp_channel(partner, instance)
#         return channel
    

#     def _find_or_create_whatsapp_channel(self, partner, instance):
#         """
#         Encontra ou cria um canal do tipo WhatsApp para um parceiro e uma instância.
#         """
#         channel = self.search([
#             ('channel_type', '=', 'whatsapp'),
#             ('whatsapp_partner_id', '=', partner.id),
#             ('whatsapp_instance_id', '=', instance.id)
#         ], limit=1)

#         if channel:
#             self._add_members_to_whatsapp_channel(channel, partner, instance)
#             return channel

#         channel = self.create({
#             'name': f"WhatsApp - {partner.name}",
#             'channel_type': 'whatsapp',
#             'whatsapp_partner_id': partner.id,
#             'whatsapp_instance_id': instance.id,
#         })
        
#         self._add_members_to_whatsapp_channel(channel, partner, instance)
#         _logger.info("Criado novo canal de WhatsApp #%s para o parceiro '%s' (ID: %s)", channel.id, partner.name, partner.id)
#         return channel