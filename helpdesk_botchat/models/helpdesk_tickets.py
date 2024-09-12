import requests
from datetime import datetime, timedelta

from odoo import _, api, fields, models, tools
from odoo.exceptions import AccessError


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"
    _description = "Helpdesk Ticket"

    def _prepare_headers(self):
        return {
            "access-token": self.env.company.token_chat , 
            "Content-type": "application/json"
        }
    
    def busca_atendimento(self):
        url_chat = 'https://api.superbotchat.com/core/v2/api/chats/list'
        # response = requests.post(
        #     url,
        #     headers=_header_busca(),
        # )
        hoje = datetime.now()
        hora = hoje + \
            timedelta(hours=-12)
        horaIni= hora.strftime("%Y-%m-%d %H:%M:%S")
        horaFim = hoje.strftime("%Y-%m-%d %H:%M:%S")
        busca = {
            # "sectorId": "string",
            # "userId": "string",
            # "number": "string",
            "contactId": "",
            "typeChat": 2,
            "status": 3,
            "dateFilters": 
            {
                "byStartDate": 
                    {
                        "start": horaIni,
                        "finish": horaFim,
                    },
                # "byEndDate": 
                #         {
                #             "start": "2024-09-10 12:15:22",
                #             "finish": "2024-09-11 19:15:22"
                #         }
            },
            "page": 0
        }
        response = requests.post(
            url_chat,
            headers= self._prepare_headers(),
            json=busca
        )
        # print(response)
        # print(response.text)
        json_resp = response.json()
        itens = []
        for linha in json_resp["chats"]:
            if not "currentUser" in linha:
                continue
            itens_det = {}
            #print (linha)
            # print (linha["attendanceId"])
            # print (linha["contact"])
            itens_det["id"] = linha["attendanceId"]
            itens_det["cliente"] = linha["contact"]["name"]
            itens_det["fone"] = linha["contact"]["number"]
            itens_det["atendente"] = linha["currentUser"]["name"]
            itens.append(itens_det)
            #print (f"Item : {item}")
        return itens
            #for item in linha["chats"]:
            #    print (item)
        
    def busca_dados_chat(self, id):
        # busca = {"chatid": id}
        url_chat_dados = f"https://api.superbotchat.com/core/v2/api/chats/{id}"
        response = requests.get(
            url_chat_dados,
            headers=self._prepare_headers(),
        )
        #    params=busca
        #import pudb;pu.db
        # print(response.url)
        #print(response)
        if response.status_code == 200:
            json_resp = response.json()
            #print(json_resp)
            mensagem = ''
            for msg in json_resp['messages']:
                # print(msg['text'])
                mensagem += msg['text'] + '<br/>'
            return mensagem
        
    def action_create_ticket(self):
        #import pudb;pu.db
        chats = self.busca_atendimento()
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
            msg = self.busca_dados_chat(id_chat["id"])
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
            self.busca_dados_chat(id_chat["id"])
            # print('-------------------------------------------------------')
            # print(f"Atendente : {id_chat['atendente']}")
            # print('-------------------------------------------------------')
        
    