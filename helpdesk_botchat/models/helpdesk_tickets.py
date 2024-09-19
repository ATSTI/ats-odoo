import requests
from datetime import datetime, timedelta

from odoo import _, api, fields, models, tools
from odoo.exceptions import AccessError
from ..chatapi import ApiChat

class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"
    _description = "Helpdesk Ticket"
        
    def action_create_ticket(self):
        api = ApiChat(
                token=(self.env.company.token_chat),
            )
        chats = api.busca_atendimento()
        for id_chat in chats:
            # print('-------------------------------------------------------')
            # print(f"Cliente : {id_chat['cliente']} , fone : {id_chat['fone']}")
            # print('-------------------------------------------------------')
            ticket = self.env['helpdesk.ticket']
            id = ticket.search([
                ('name', '=', id_chat["id"])
            ])
            if id:
                continue
            user = self.env['res.users'].search([
                ('name', 'ilike', id_chat["atendente"])
            ])
            fone = id_chat["fone"]
            client = self.env['res.partner'].search([
                "|",('name', 'ilike', id_chat["cliente"]),
                ('phone', 'like', fone[len(fone)-8:])
            ])
            msg = api.busca_dados_chat(id_chat["id"])
            vals = {
                "name": id_chat["id"],
                "description": msg,
                "stage_id": 4,
            }
            if user:
                vals["user_id"] = user.id
            if client:
                vals["partner_id"] = client.id
            t = ticket.create(vals)
            t._onchange_partner_id()
            api.busca_dados_chat(id_chat["id"])
            # print('-------------------------------------------------------')
            # print(f"Atendente : {id_chat['atendente']}")
            # print('-------------------------------------------------------')
        
    