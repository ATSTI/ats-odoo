# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta, date
import hmac
import hashlib
import json
import requests
import time

class ProducTemplate(models.Model):
    _inherit = "product.template"

    shopee = fields.Boolean(
        string='Vende Shopee?',
        default=False,
        )
    shopee_item_id = fields.Char('Id do Item')
    margin_shopee = fields.Char('Margem Shopee')
    title_shopee = fields.Char('Titulo do Produto')
    price_shopee = fields.Float('Preço Shopee')
    qtd_shopee = fields.Float('Quantidade Disponivel Shopee')
    shopee_sku = fields.Char('SKU Shopee')
    image_shopee = fields.Boolean('Usar mesma imagem do Odoo?')
    image_shopee_url = fields.Char('URL da Imagem Shopee')
    shopee_config_id = fields.Many2one('shopee.config', 'Shopee')

    #url_ini = "https://openplatform.shopee.com.br" 
    # url_ini = "https://partner.test-stable.shopeemobile.com"

    @api.onchange('shopee')
    def onchange_shopee(self):
        if self.shopee == True:
            self.title_shopee = self.name
            self.shopee_sku = self.default_code
            self.price_shopee = self.list_price 
            self.qtd_shopee = 1

    def atualiza_preco_shopee(self):
        if self.shopee_config_id.shop_real == True:
            url_ini = "https://openplatform.shopee.com.br"
        if self.shopee_config_id.shop_real == False:
            url_ini = "https://partner.test-stable.shopeemobile.com"
        if self.shopee_config_id.expire_date_token and self.shopee_config_id.expire_date_token < datetime.now():
            self.shopee_config_id.action_gera_acess_token()
            print("TOKEN GERADO")
        if self.shopee_item_id:
            timest = str(int(time.time()))
            sp = self.shopee_config_id
            path = '/api/v2/product/update_price'
            tmp_base_string = "%s%s%s%s%s" % (sp.shopee_partner_id, path, timest, sp.access_token, sp.shopee_id)
            base_string = tmp_base_string.encode()
            sign = hmac.new(sp.shopee_partner_key.encode(), base_string, hashlib.sha256).hexdigest()
            path_attr = "/api/v2/product/update_price?access_token=%s&partner_id=%s&shop_id=%s&sign=%s&timestamp=%s" %(sp.access_token, sp.shopee_partner_id, sp.shopee_id, sign, timest)
            url = url_ini + path_attr
            payload = json.dumps({
                "item_id": int(self.shopee_item_id),
                "price_list": [
                    {
                        "item_id": int(self.shopee_item_id),
                        "original_price": self.price_shopee,
                    }
                ]
            })

            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.post(url, headers=headers, data=payload)
            data = response.json()
            if data.get('error'):
                raise UserError(_(f"(Atualize a Pagina e Tente Novamente) Erro ao atualizar preço: {data['debug_message']}"))
            else:
                raise UserError(_(f"Preço Atualizado Com Sucesso!"))
        else:
            self.procura_item_existente()

    def atualiza_stock_shopee(self):
        if self.shopee_config_id.shop_real == True:
            url_ini = "https://openplatform.shopee.com.br"
        if self.shopee_config_id.shop_real == False:
            url_ini = "https://partner.test-stable.shopeemobile.com"
        if self.shopee_config_id.expire_date_token and self.shopee_config_id.expire_date_token < datetime.now():
            self.shopee_config_id.action_gera_acess_token()
            print("TOKEN GERADO")
        if self.shopee_item_id:
            timest = str(int(time.time()))
            sp = self.shopee_config_id
            path = '/api/v2/product/update_stock'
            tmp_base_string = "%s%s%s%s%s" % (sp.shopee_partner_id, path, timest, sp.access_token, sp.shopee_id)
            base_string = tmp_base_string.encode()
            sign = hmac.new(sp.shopee_partner_key.encode(), base_string, hashlib.sha256).hexdigest()
            path_attr = "/api/v2/product/update_stock?access_token=%s&partner_id=%s&shop_id=%s&sign=%s&timestamp=%s" %(sp.access_token, sp.shopee_partner_id, sp.shopee_id, sign, timest)
            url = url_ini + path_attr 
            payload = json.dumps({
                "item_id": int(self.shopee_item_id),
                "stock_list": [
                    {
                        "seller_stock": [
                            {
                            "item_id": int(self.shopee_item_id),
                            "stock": int(self.qtd_shopee)
                            }
                        ]
                    }
                ]
            })

            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.post(url, headers=headers, data=payload)
            data = response.json()
            if data.get('error'):
                raise UserError(_(f"(Atualize a Pagina e Tente Novamente) Erro ao atualizar estoque: {data['debug_message']}"))
            else:
                raise UserError(_(f"Quantidade Atualizada Com Sucesso!"))
        else:
            self.procura_item_existente()
            
    def procura_item_existente(self):
        if self.shopee_config_id.shop_real == True:
            url_ini = "https://openplatform.shopee.com.br"
        if self.shopee_config_id.shop_real == False:
            url_ini = "https://partner.test-stable.shopeemobile.com"
        timest = str(int(time.time()))
        sp = self.shopee_config_id
        path = '/api/v2/product/get_item_list'
        tmp_base_string = "%s%s%s%s%s" % (sp.shopee_partner_id, path, timest, sp.access_token, sp.shopee_id)
        base_string = tmp_base_string.encode()
        sign = hmac.new(sp.shopee_partner_key.encode(), base_string, hashlib.sha256).hexdigest()
        data_i = int((datetime(2025, 1, 1, 15, 30)).timestamp())
        data_f = int((datetime.now() + timedelta(hours=1)).timestamp())
        path_attr = "/api/v2/product/get_item_list?access_token=%s&offset=0&page_size=10&item_status=NORMAL&partner_id=%s&shop_id=%s&sign=%s&timestamp=%s&update_time_from=%s&update_time_to=%s" %(sp.access_token, sp.shopee_partner_id,sp.shopee_id, sign, timest, data_i, data_f)
        payload={}
        headers = {}
        url = url_ini + path_attr
        response = requests.request("GET",url,headers=headers, data=payload, allow_redirects=False)
        data = response.json()
        for rs in data['response']['item']:
            item = rs['item_id']
            path = '/api/v2/product/get_item_base_info'
            tmp_base_string = "%s%s%s%s%s" % (sp.shopee_partner_id, path, timest, sp.access_token, sp.shopee_id)
            base_string = tmp_base_string.encode()
            sign = hmac.new(sp.shopee_partner_key.encode(), base_string, hashlib.sha256).hexdigest()
            path_attr = "/api/v2/product/get_item_base_info?access_token=%s&need_complaint_policy=true&need_tax_info=true&item_id_list=%s&partner_id=%s&shop_id=%s&sign=%s&timestamp=%s" %(sp.access_token, item, sp.shopee_partner_id, sp.shopee_id, sign, timest)
            payload = {}
            headers = {}
            url = url_ini + path_attr
            response = requests.get(url,headers=headers, data=payload, allow_redirects=False)
            data = response.json()
            for it in data['response']['item_list']:
                sku = it['item_sku']
                if sku == self.shopee_sku:
                    self.shopee_item_id = it['item_id']
                    break
            if self.shopee_item_id:
                break


    def action_envia_produto_shopee(self):
        return True
        # FUNÇÃO DE ADICIONAR PEDIDO VIA ODOO REMOVIDO ( PEDIDO DA FELICITA)
        # FUNCIONA CORRETAMENTE
        timest = str(int(time.time()))
        if self.shopee_config_id.expire_date_token and self.shopee_config_id.expire_date_token < datetime.now():
            self.shopee_config_id.action_gera_acess_token()
            print("TOKEN GERADO")
        if self.shopee_item_id:
            url = "https://partner.test-stable.shopeemobile.com/api/v2/product/update_item?access_token=4f545562754445496347644362725673&partner_id=1278861&shop_id=134713&sign=3b178da2df2be7f455d5b9071849e3b46f8057c08fb683dc53d9de9945d92d34&timestamp=1748544355"

            payload=json.dumps({
            "brand": {
                "brand_id": 0,
                "original_brand_name": "Sem Marca"
            },
            "category_id": 102064,
            "condition": "USED",
            "description": "ITEM ATUALIZADO VIA ODOO",
            "dimension": {
                "package_height": 13,
                "package_length": 12,
                "package_width": 14
            },
            "item_id": self.shopee_item_id,
            "item_name": self.title_shopee,
            "item_sku": self.shopee_sku,
            "item_status": "UNLIST",
            "logistic_info": [
                {
                "enabled": True,
                "logistic_id": 90003
                }
            ],
            "tax_info": {
                "hs_code": "-",
                "tax_code": "-"
            },
            "weight": 1
            })
            headers = {
            'Content-Type': 'application/json'
            }
            response = requests.request("POST",url,headers=headers, data=payload, allow_redirects=False)
            data = response.json()
            if data.get('error'):
                raise UserError(_(f"(Atualize a Pagina e Tente Novamente) Erro ao atualizar produto: {data['debug_message']}"))
            else:
                raise UserError(_(f"Produto Atualizado Com Sucesso!"))
        sp = self.shopee_config_id
        path = '/api/v2/product/add_item'
        tmp_base_string = "%s%s%s%s%s" % (sp.shopee_partner_id, path, timest, sp.access_token, sp.shopee_id)
        base_string = tmp_base_string.encode()
        sign = hmac.new(sp.shopee_partner_key.encode(), base_string, hashlib.sha256).hexdigest()
        path_attr = "/api/v2/product/add_item?access_token=%s&partner_id=%s&shop_id=%s&sign=%s&timestamp=%s" %(sp.access_token, sp.shopee_partner_id, sp.shopee_id, sign, timest)
        url = self.url_ini + path_attr

        payload=json.dumps({
        "brand": {
            "brand_id": 0,
            "original_brand_name": "Sem Marca"
        },
        "category_id": 102064,
        "condition": "NEW",
        "description": "ITEM ADICIONADO VIA ODOO",
        "dimension": {
            "package_height": 11,
            "package_length": 11,
            "package_width": 11
        },
        "image": {
            "image_id_list": [
            "sg-11134201-7r98o-mair93brwdgodb",
            "sg-11134201-7r98o-mair93brwdgodb"
            ]
        },
        "item_name": self.title_shopee,
        "item_sku": self.shopee_sku,
        "item_status": "NORMAL",
        "logistic_info": [
            {
            "enabled": True,
            "logistic_id": 90003
            }
        ],
        "original_price": self.price_shopee,
        "seller_stock": [
            {
            "stock": int(self.qtd_shopee)
            }
        ],
        "weight": 11,
        })
        headers = {
        'Content-Type': 'application/json'
        }
        response = requests.request("POST",url,headers=headers, data=payload, allow_redirects=False)
        data = response.json()
        if data.get('error'):
            raise UserError(_(f"Erro ao adicionar produto: {data['debug_message']}"))
        else:
            self.shopee_item_id = data['response']['item_id']
        return True