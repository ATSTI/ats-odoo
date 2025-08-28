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
    # margin_shopee = fields.Char('Margem Shopee')
    title_shopee = fields.Char('Titulo do Produto')
    price_shopee = fields.Float('Preço Shopee')
    qtd_shopee = fields.Float('Quantidade Disponivel Shopee')
    shopee_sku = fields.Char('SKU Shopee')
    image_shopee = fields.Boolean('Usar mesma imagem do Odoo?')
    image_shopee_url = fields.Char('URL da Imagem Shopee')
    shopee_config_id = fields.Many2one('shopee.config', 'Shopee')

    #url_ini = "https://openplatform.shopee.com.br" 
    # url_ini = "https://partner.test-stable.shopeemobile.com"

    # Pc = 50,00 + T = Taxa por venda 6,00 + Cv = comissão de venda 15% + Ml = margem de lucro 45%
    # Formula: Vt = Pc + T + Cv + Ml
    # Pc; Preço de Custo ODOO
    # T; Taxa fixa de cada plataforma
    # Cv; Comissão de Venda da plataforma
    # Ml; Margem de lucro da Felicita
    # Vt; Valor de Venda Total


    @api.depends('standard_price')
    def calcula_valor_venda_shopee(self):
        #Por enquanto essa aplicação, apresentar para eles e ver...
        pc = self.standard_price
        t = self.shopee_config_id.taxa_shopee
        pc = pc + t
        cv = self.shopee_config_id.margin_shopee/100 * pc
        ml = self.shopee_config_id.margem_lucro/100 * pc
        Vt = pc + cv + ml
        self.price_shopee = Vt

    @api.onchange('standard_price')
    def onchange_standard_price_shopee(self):
        if self.shopee == True:
            self.calcula_valor_venda_shopee()

    @api.onchange('shopee')
    def onchange_shopee(self):
        if self.shopee == True:
            self.title_shopee = self.name
            self.shopee_sku = self.default_code 
            self.qtd_shopee = 1
            self.calcula_valor_venda_shopee()

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
        sp = self.shopee_config_id

        # URL da Shopee, ambiente real ou sandbox
        url_ini = "https://openplatform.shopee.com.br" if sp.shop_real else "https://partner.test-stable.shopeemobile.com"

        # Define intervalo de data amplo (últimos 3 anos)
        data_i = int((datetime.now() - timedelta(days=3*365)).timestamp())
        data_f = int((datetime.now() + timedelta(hours=1)).timestamp())

        offset = 0
        if self.shopee_config_id.shop_real == True:
            url_ini = "https://openplatform.shopee.com.br"
        if self.shopee_config_id.shop_real == False:
            url_ini = "https://partner.test-stable.shopeemobile.com"
        page_size = 100
        for item_status in ["NORMAL", "UNLIST", "SOLD_OUT"]:
            offset = 0
            while True:
                timest = str(int(time.time()))
                path = '/api/v2/product/get_item_list'
                base_string = f"{sp.shopee_partner_id}{path}{timest}{sp.access_token}{sp.shopee_id}".encode()
                sign = hmac.new(sp.shopee_partner_key.encode(), base_string, hashlib.sha256).hexdigest()

                url = (
                    f"{url_ini}{path}?access_token={sp.access_token}&offset={offset}&page_size={page_size}"
                    f"&item_status={item_status}&partner_id={sp.shopee_partner_id}&shop_id={sp.shopee_id}"
                    f"&sign={sign}&timestamp={timest}&update_time_from={data_i}&update_time_to={data_f}"
                )

                response = requests.get(url)
                if response.status_code != 200:
                    print(f"❌ Erro na requisição: {response.status_code} - {response.text}")
                    break

                data = response.json()
                items = data.get('response', {}).get('item', [])
                if not items:
                    break

                item_ids = [str(item['item_id']) for item in items]

                for i in range(0, len(item_ids), 50):  # Shopee só aceita até 50 item_ids por vez
                    batch = item_ids[i:i+50]
                    item_id_list_str = ",".join(batch)

                    timest = str(int(time.time()))
                    path_info = '/api/v2/product/get_item_base_info'
                    base_string = f"{sp.shopee_partner_id}{path_info}{timest}{sp.access_token}{sp.shopee_id}".encode()
                    sign = hmac.new(sp.shopee_partner_key.encode(), base_string, hashlib.sha256).hexdigest()

                    url_info = (
                        f"{url_ini}{path_info}?access_token={sp.access_token}&need_complaint_policy=true"
                        f"&need_tax_info=true&item_id_list={item_id_list_str}&partner_id={sp.shopee_partner_id}"
                        f"&shop_id={sp.shopee_id}&sign={sign}&timestamp={timest}"
                    )

                    response_info = requests.get(url_info)
                    if response_info.status_code != 200:
                        print(f"❌ Erro ao buscar info dos itens: {response_info.status_code} - {response_info.text}")
                        continue

                    item_data = response_info.json()
                    for it in item_data.get('response', {}).get('item_list', []):
                        # if str(it['item_id']) == "23797586082":/
                        sku = it.get('item_sku', '')
                        if sku == self.shopee_sku:
                            self.shopee_item_id = it['item_id']
                            print(f"✅ Item encontrado: {sku} → ID: {self.shopee_item_id}")
                            return
                        if it['has_model']:
                            path_model = '/api/v2/product/get_model_list'
                            timest = str(int(time.time()))
                            base_string = f"{sp.shopee_partner_id}{path_model}{timest}{sp.access_token}{sp.shopee_id}".encode()
                            sign = hmac.new(sp.shopee_partner_key.encode(), base_string, hashlib.sha256).hexdigest()

                            url_model = (
                                f"{url_ini}{path_model}?access_token={sp.access_token}&item_id={it['item_id']}"
                                f"&partner_id={sp.shopee_partner_id}&shop_id={sp.shopee_id}&sign={sign}&timestamp={timest}"
                            )

                            response_model = requests.get(url_model)
                            data_model = response_model.json()
                            for dm in data_model.get('response', {}).get('model', {}):
                                if str(dm['model_sku']) == self.shopee_sku:
                                    self.shopee_item_id = it['item_id']
                                    # self.shopee_model_id = dm['model']['model_id']
                                    print(f"✅ SKU de variação encontrado: {dm['model_sku']} → item_id: {self.shopee_item_id}")
                                    return

                offset += page_size

            print("❌ Item não encontrado.")

    def action_envia_produto_shopee(self):
        return True
        # FUNÇÃO DE ADICIONAR PEDIDO VIA ODOO REMOVIDO (PEDIDO DA FELICITA)
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