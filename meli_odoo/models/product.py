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
    # FIXA POR ENQUANTO category_meli = fields.Char('Categoria Mercado Livre')
    price_meli = fields.Float('Preço Mercado Livre')
    qtd_meli = fields.Float('Quantidade Disponivel Mercado Livre')
    guarantee_meli = fields.Selection([
        ('0', 'Sem Garantia'),
        ('30', '30 dias'),
        ('60', '60 dias'),
        ('90', '90 dias'),
        ('120', '120 dias'),
        ('180', '180 dias'),
        ('360', '360 dias'),
    ], string='Garantia do Comprador', default='0')
    image_meli = fields.Boolean('Usar mesma imagem do Odoo?')
    image_meli_url = fields.Char('URL da Imagem Mercado Livre')
    meli_config_id = fields.Many2one('meli.config', 'Mercado Livre')


    def action_envia_produto(self):
        import pudb;pu.db
        if self.meli_config_id.expire_date_token and self.meli_config_id.expire_date_token < datetime.now():
            self.meli_config_id.action_gera_acess_token()
            print("TOKEN GERADO")
        # FAZENDO ATUALIZAÇÃO DO PRODUTO
        if self.meli_item_id:
            headers = {
                'Authorization': 'Bearer %s' %(self.meli_config_id.access_token),
                'Content-Type': 'application/x-www-form-urlencoded',
            }

            data = '{\
                status: closed\
            }'.encode()
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
            data = response.json()
            item = response.json()
            self.meli_item_id = item['id']
        # ENVIANDO PRODUTO NOVO
        else:
            headers = {
                'Authorization': 'Bearer %s' %(self.meli_config_id.access_token),
                'Content-Type': 'application/x-www-form-urlencoded',
            }
            data = '{  \
                "title":%s,\
                "category_id":"MLB256817",\
                "price":%s,\
                "currency_id":"BRL",\
                "available_quantity":%s,\
                "buying_mode":"buy_it_now",\
                "condition":"new",\
                "listing_type_id":"gold_pro",\
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
                }\
            }' %(self.title_meli, self.price_meli, self.qtd_meli, self.guarantee_meli)
            data = data.encode() 
            response = requests.post('https://api.mercadolibre.com/items', headers=headers, data=data)
            item = response.json()
            self.meli_item_id = item['id']
        return True
