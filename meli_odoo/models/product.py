# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta, date
import requests


class ProducTemplate(models.Model):
    _inherit = "product.template"

    meli = fields.Boolean(
        string='Vende Mercado Livre?',
        default=False,
        )
    meli_item_id = fields.Char('Id do Item')
    margin_meli = fields.Char('Margem Mercado Livre')
    title_meli = fields.Char('Titulo do Produto')
    meli_sku = fields.Char('SKU Mercado Livre')
    price_meli = fields.Float('Preço Mercado Livre')
    qtd_meli = fields.Float('Quantidade Disponivel Mercado Livre')
    # category_meli = fields.Selection([
    #     ('MLB256813', 'Artigos para Festas > Outros'),
    #     ('MLB256817', 'Decorações para Festas > Outros'),
    #     ('MLB457464', 'Corantes Comestíveis'),
    #     ('MLB40189', 'Lembrancinhas'),
    #     #TODO ADICIONAR TODAS CATEGORIAS UTILIZADAS NO MERCADO LIVRE
    # ],'Categoria Mercado Livre')
    # guarantee_meli = fields.Selection([
    #     ('0', 'Sem Garantia'),
    #     ('30', '30 dias'),
    #     ('60', '60 dias'),
    #     ('90', '90 dias'),
    #     ('120', '120 dias'),
    #     ('180', '180 dias'),
    #     ('360', '360 dias'),
    # ], string='Garantia do Comprador', default='0')
    # image_meli = fields.Char('Imagem Mercado Livre')
    meli_config_id = fields.Many2one('meli.config', 'Mercado Livre')


    @api.onchange('meli')
    def onchange_meli(self):
        if self.meli == True:
            self.title_meli = self.name
            self.meli_sku = self.default_code
            self.price_meli = self.list_price 
            self.qtd_meli = 1

    def action_envia_produto_meli(self):
        if self.meli_config_id.expire_date_token and self.meli_config_id.expire_date_token < datetime.now():
            self.meli_config_id.action_gera_acess_token()
            print("TOKEN GERADO")
        if self.meli_item_id:
            headers = {
                'Authorization': 'Bearer %s' %(self.meli_config_id.access_token),
                'Content-Type': 'application/json',
            }

            data = "{\
                status: closed}"
            data = data.encode()
            url = f'https://api.mercadolibre.com/items/{self.meli_item_id}'
            response = requests.put(url, headers=headers, data=data)
            if response.status_code == 200:
                print("PRODUTO FECHADO")
            headers = {
                'Authorization': 'Bearer %s' %(self.meli_config_id.access_token),
                'Content-Type': 'application/json',
            }

            data = '{ \
                price: %s, \
                quantity: %s, \
                listing_type_id:gold_special\
            }' %(self.price_meli, self.qtd_meli)
            data = data.encode()
            url = f'https://api.mercadolibre.com/items/{self.meli_item_id}/relist'
            response = requests.post(url, headers=headers, data=data)
            item = response.json()
            self.meli_item_id = item['id']
        else:
            user_id = self.meli_config_id.user_id
            url = f"https://api.mercadolibre.com/users/{user_id}/items/search"
            headers = {
                "Authorization": f"Bearer {self.meli_config_id.access_token}"
            }

            response = requests.get(url, headers=headers)
            data = response.json()
            for item_id in data.get("results", []):
                url = f"https://api.mercadolibre.com/items/{item_id}"
                headers = {
                    "Authorization": f"Bearer {self.meli_config_id.access_token}"
                }

                response = requests.get(url, headers=headers)
                data = response.json()
                if data.get("status") == "active":
                    for att in data.get("attributes"):
                        if att['id'] == "SELLER_SKU":
                            sku = att["value_name"]
                            if sku == self.meli_sku:
                                self.meli_item_id = item_id
                    if data.get("seller_custom_field"):
                        sku = data.get("seller_custom_field")
                        if sku == self.meli_sku:
                            self.meli_item_id = item_id
                else:
                    print("Produto INATIVO", item_id)
        return True
        # ESSA PARTE FOI REMOVIDA POR PEDIDO DA PROPRIA FELICITA
        # ESSA É A FUNÇÃO QUE MANDA O PRODUTO PARA O MERCADO LIVRE       
        headers = {
            'Authorization': 'Bearer %s' %(self.meli_config_id.access_token),
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        data = '{  \
            "title":%s,\
            "category_id":%s,\
            "price":%s,\
            "currency_id":"BRL",\
            "available_quantity":%s,\
            "buying_mode":"buy_it_now",\
            "condition":"new",\
            "listing_type_id":"gold_special",\
            "sale_terms":[\
                {\
                    "id":"WARRANTY_TYPE",\
                    "value_name":"Garantia do vendedor"\
                },\
                {\
                    "id":"WARRANTY_TIME",\
                    "value_name":"%s Dias"   \
                }\
            ],\
            "pictures":[{\
                "source":"https://example.com/imagem.jpg"\
                }\
            ], \
            "attributes":[\
                {\
                    "id":"BRAND",\
                    "value_name":"Sem Marca"\
                },\
            ],\
            "shipping": {\
                "mode": "me2",\
                "local_pick_up": false,\
                "free_shipping": false\
            },\
            "seller_custom_field": "%s"\
        }' %(self.title_meli, self.category_meli ,self.price_meli, self.qtd_meli, self.guarantee_meli, self.meli_sku)
        data = data.encode() 
        response = requests.post('https://api.mercadolibre.com/items', headers=headers, data=data)
        item = response.json()
        print (response.text)
        self.meli_item_id = item['id']
