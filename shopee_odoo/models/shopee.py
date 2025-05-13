# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import requests
import json
import time
import hmac
import hashlib

class ShopeeConfig(models.Model):
    _name = 'shopee.config'
    _description = "Shopee Config"

    name = fields.Char('Nome da Loja', required=True)
    shopee_id = fields.Char('Shopee ID', required=True)
    access_token = fields.Char('Access Token', readonly=True)
    expire_date_token = fields.Datetime('Expire Date Token', readonly=True)
    refresh_token = fields.Char('Refresh Token', required=True)
    refresh_token_security = fields.Char('Refresh Token security', invisible=True, readonly=True)
    shopee_partner_id = fields.Char('Partner ID', required=True)
    shopee_partner_key = fields.Char('Partner Key', required=True)
    
    #nao é campo
    url_ini = "https://partner.shopeemobile.com" 
    # url_ini = "https://partner.test-stable.shopeemobile.com"

    def action_gera_acess_token(self):
        timest = str(int(time.time()))
        path = "/api/v2/auth/access_token/get"
        tmp_base_string = "%s%s%s" % (self.shopee_partner_id, path, timest)
        base_string = tmp_base_string.encode()
        sign = hmac.new(self.shopee_partner_key.encode(), base_string, hashlib.sha256).hexdigest()

        payload=json.dumps({
        "partner_id": int(self.shopee_partner_id),
        "refresh_token": self.refresh_token,
        "shop_id": int(self.shopee_id)
        })
        headers = {
        'Content-Type': 'application/json'
        }
        path_cat = "/api/v2/auth/access_token/get?partner_id=%s&sign=%s&timestamp=%s" %(self.shopee_partner_id, sign, timest)
        url = self.url_ini + path_cat
        response = requests.request("POST",url,headers=headers, data=payload, allow_redirects=False)
        res = response.json()
        expire_in = res['expire_in']
        validade = datetime.now() + timedelta(seconds=expire_in)
        self.expire_date_token = validade
        if response.status_code == 200:
            self.access_token = res['access_token']
            self.refresh_token = res['refresh_token']
            self.refresh_token_security = res['refresh_token']
        else:
            raise UserError("Erro ao gerar o access token")
        
    def cron_execute_pega_faturas(self):
        lj = self.search([])
        for loja in lj:
            loja.action_pega_faturas_shopee()

    def action_pega_faturas_shopee(self):
        # import pudb;pu.db
        if self.expire_date_token and self.expire_date_token < datetime.now():
            self.action_gera_acess_token()
            print("TOKEN GERADO")
        timest = str(int(time.time()))
        path = "/api/v2/order/get_order_list"
        tmp_base_string = "%s%s%s%s%s" % (self.shopee_partner_id, path, timest, self.access_token, self.shopee_id)
        base_string = tmp_base_string.encode()
        sign = hmac.new(self.shopee_partner_key.encode(), base_string, hashlib.sha256).hexdigest()
        payload={}
        headers = {
        }
        # 1607235072&time_range_field=create_time&time_to=1608271872
        data_i = datetime.now() - timedelta(days=2)
        data_inicio = int(data_i.timestamp())
        data_fim = int(time.time())
        data_f = datetime.now() + timedelta(days=1)
        data_fim = int(data_f.timestamp())
        # data_fim = 1608271872
        # order_status=READY_TO_SHIP&  tirei do link abaixo pq nao trazia
        path_cat = "?access_token=%s&cursor=&page_size=20&partner_id=%s&request_order_status_pending=true&response_optional_fields=order_status&shop_id=%s&sign=%s&time_from=%s&time_range_field=create_time&time_to=%s&timestamp=%s" %(self.access_token,self.shopee_partner_id,self.shopee_id,sign,data_inicio,data_fim,timest)
        url = self.url_ini + path + path_cat
        response = requests.request("GET",url,headers=headers, data=payload, allow_redirects=False)
        od_list = response.json()
        for od in od_list['response']['order_list']:
            order_sn = str(od['order_sn'])
            sale_exists = self.env['sale.order'].search([
                ('name', '=', str(od['order_sn'])),
            ])
            if od['order_status'] == "UNPAID" or od['order_status'] == "CANCELLED":
                print("PEDIDO CANCELADO OU NAO PAGO")
                continue
            if od['order_status'] == "PROCESSED":
                print("PEDIDO JÁ ENVIADO")
                continue
            if sale_exists:
                continue
            # PARTE QUE TRAS AS FATURAS CRIADAS E AS RESPECTIVAS INFORMACOES
            if od['order_status'] == "READY_TO_SHIP":
                path = "/api/v2/order/get_order_detail"
                tmp_base_string = "%s%s%s%s%s" % (self.shopee_partner_id, path, timest, self.access_token, self.shopee_id)
                base_string = tmp_base_string.encode()
                sign = hmac.new(self.shopee_partner_key.encode(), base_string, hashlib.sha256).hexdigest()
                payload={}
                headers = {
                }
                optional = "total_amount,buyer_user_id,buyer_username,recipient_address,buyer_cpf_id,item_list"
                path_cat = "?access_token=%s&order_sn_list=%s&partner_id=%s&request_order_status_pending=true&response_optional_fields=%s&shop_id=%s&sign=%s&timestamp=%s" %(self.access_token,order_sn, self.shopee_partner_id,optional,self.shopee_id,sign,timest)
                url = self.url_ini + path + path_cat
                response = requests.request("GET",url,headers=headers, data=payload, allow_redirects=False)
                od_detail = response.json()
                order_name = ''
                prd_id = ''
                prd_qtd = ''
                prd_price = ''
                for z in od_detail['response']['order_list']:
                    order_line = []
                    for key, value in z.items():
                        if key == "item_list":
                            print("ITEMS : ----------------------")
                            for itens in z["item_list"]:
                                for key, value in itens.items():
                                    print(f"---------------ITEM : {key}--{value}")
                                    prd_sku = itens['item_sku']
                                    prd_id = itens['item_id']
                                    prd_qtd = itens['model_quantity_purchased']
                                    prd_price = itens['model_original_price']
                                    prd_name = itens['item_name']
                                    prod = self.env["product.product"].search([
                                        ('default_code', '=', prd_sku),
                                    ])
                                if not prod:
                                    prod = self.env["product.product"].search([
                                        ('default_code', '=', 999999),
                                    ])
                                    prd_name = f"[{prd_sku}] {prd_name}"
                                else:
                                    prod.shopee = True
                                    prod.shopee_sku = prd_sku
                                    prod.title_shopee = prd_name
                                    prod.shopee_config_id = self.id
                                    prod.shopee_item_id = prd_id
                                vals_line = {
                                    'product_id': prod.id,
                                    'product_uom_qty': prd_qtd,
                                    'price_unit': prd_price,
                                    'name': prd_name,
                                }
                                order_line.append((0, 0,vals_line))
                        elif key == "recipient_address":
                            print("Endereço : ===========================================")
                            for key, value in z["recipient_address"].items():
                                print(f"ENDERECO : {key}-{value}")
                                if key == "full_address":
                                    street = value
                                    st_n = value
                                    street_n = st_n[:st_n.find(",")]
                        else:
                            print(f"{key}--{value}")
                            order_name = str(z['order_sn'])
                            id_buyer = str(z['buyer_user_id'])
                            name_buyer = str(z['buyer_username'])
                            cpf_b = str(z['buyer_cpf_id'])
                            if len(cpf_b) < 11:
                                cpf_b = cpf_b.zfill(11)
                            cpf = '{}.{}.{}-{}'.format(cpf_b[:3], cpf_b[3:6], cpf_b[6:9], cpf_b[9:])
                    print("PEDIDO CRIADO")
                    pr = self.env["res.partner"].search([
                        ('cnpj_cpf', '=', cpf),
                    ])
                    if not pr:
                        vals_pr = {
                            'name': name_buyer,
                            'cnpj_cpf': cpf,
                            'ref': id_buyer,
                            'street_name':  "Endereço Bloqueado (Cadastrar)", #street[:street.find(",")],
                            # 'street_number': street_n[:street_n.find(",")],
                            # 'district': z['recipient_address']['district'],
                            # 'city': z['recipient_address']['city'],
                            'state_id': self.env['res.country.state'].search([('name', '=', z['recipient_address']['state'])], limit=1).id,
                            # 'zip': z['recipient_address']['zipcode']
                        }
                        pr = self.env['res.partner'].create(vals_pr)
                        if pr.cnpj_cpf:
                            pr._onchange_cnpj_cpf()
                    vals={
                        "name": order_name,
                        "partner_id": pr.id,
                    }
                    
                    sale = self.env['sale.order'].create(vals)
                    
                    if len(order_line):
                        sale['order_line'] = order_line
        return True

