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
    # FIXA POR ENQUANTO category_shopee = fields.Char('Categoria Shopee')
    price_shopee = fields.Float('Preço Shopee')
    qtd_shopee = fields.Float('Quantidade Disponivel Shopee')
    shopee_sku = fields.Char('SKU Shopee')
    image_shopee = fields.Boolean('Usar mesma imagem do Odoo?')
    image_shopee_url = fields.Char('URL da Imagem Shopee')
    shopee_config_id = fields.Many2one('shopee.config', 'Shopee')

    # url_ini = "https://openplatform.shopee.com.br" 
    url_ini = "https://partner.test-stable.shopeemobile.com"
    timest = str(int(time.time()))

    def action_envia_produto(self):
        if self.shopee_config_id.expire_date_token and self.shopee_config_id.expire_date_token < datetime.now():
            self.shopee_config_id.action_gera_acess_token()
            print("TOKEN GERADO")
        if self.shopee_item_id:
            raise UserError(_('Produto já cadastrado na Shopee!')) #FAZER MESMA ROTINA DO MELI, DE DAR UPDATE NO PRODUTO
        sp = self.shopee_config_id
        path = '/api/v2/product/add_item'
        tmp_base_string = "%s%s%s%s%s" % (sp.shopee_partner_id, path, self.timest, sp.access_token, sp.shopee_id)
        base_string = tmp_base_string.encode()
        sign = hmac.new(sp.shopee_partner_key.encode(), base_string, hashlib.sha256).hexdigest()
        path_attr = "/api/v2/product/add_item?access_token=%s&partner_id=%s&shop_id=%s&sign=%s&timestamp=%s" %(sp.access_token, sp.shopee_partner_id, sp.shopee_id, sign, self.timest)
        url = self.url_ini + path_attr

        payload=json.dumps({
        "brand": {
            "brand_id": 0,
            "original_brand_name": "Sem marca"
        },
        "category_id": 102064,
        "condition": "NEW",
        "description": self.title_shopee,
        "dimension": {
            "package_height": 11,       #VARIAVEL
            "package_length": 11,
            "package_width": 11
        },
        "image": {
            "image_id_list": [
            "sg-11134201-7r98o-m95yi81xz9vbcb",     #variavel   
            "sg-11134201-7r98o-m95yi81xz9vbcb"
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
        "pre_order": {
            "is_pre_order": False
        },
        "seller_stock": [
            {
            "stock": int(self.qtd_shopee),
            }
        ],
        "tax_info": {
            "hs_code": "-",
            "tax_code": "-"
        },
        "weight": 1.1,  #VARIAVEL
        "wholesale": [
            {
            "max_count": 100,
            "min_count": 10,
            "unit_price": 28.3
            }
        ]
        })
        headers = {
        'Content-Type': 'application/json'
        }
        response = requests.request("POST",url,headers=headers, data=payload, allow_redirects=False)
        data = response.json()
        for item in data['response']:
            self.shopee_item_id = item['item_id']
        print(response.text)
        return True