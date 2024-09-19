import json
import requests
from datetime import datetime, timedelta

class ApiChat(object):
    
    def __init__(self, token):
        self._token = token

    def _prepare_headers(self):
        return {
            "access-token": self._token , 
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
