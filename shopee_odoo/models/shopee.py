# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import requests
import json
import base64
import tempfile
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
    shop_real = fields.Boolean('Loja Real?', default=True)
    
    # url_ini = "https://partner.shopeemobile.com" 

    def action_gera_acess_token(self):
        if self.shop_real == True:
            url_ini = "https://openplatform.shopee.com.br"
        if self.shop_real == False:
            url_ini = "https://partner.test-stable.shopeemobile.com"
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
        url = url_ini + path_cat
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
        if self.shop_real == True:
            url_ini = "https://openplatform.shopee.com.br"
        if self.shop_real == False:
            url_ini = "https://partner.test-stable.shopeemobile.com"
        if self.expire_date_token and self.expire_date_token < datetime.now():
            self.action_gera_acess_token()
            # print("TOKEN GERADO")
        timest = str(int(time.time()))
        path = "/api/v2/order/get_order_list"
        tmp_base_string = "%s%s%s%s%s" % (self.shopee_partner_id, path, timest, self.access_token, self.shopee_id)
        base_string = tmp_base_string.encode()
        sign = hmac.new(self.shopee_partner_key.encode(), base_string, hashlib.sha256).hexdigest()
        payload={}
        headers = {
        }
        # 1607235072&time_range_field=create_time&time_to=1608271872
        data_i = datetime.now() - timedelta(days=1)
        data_inicio = int(data_i.timestamp())
        data_fim = int(time.time())
        data_f = datetime.now() + timedelta(hours=1)
        data_fim = int(data_f.timestamp())
        # data_fim = 1608271872
        # order_status=READY_TO_SHIP&  tirei do link abaixo pq nao trazia
        path_cat = "?access_token=%s&cursor=&page_size=20&partner_id=%s&request_order_status_pending=true&response_optional_fields=order_status&shop_id=%s&sign=%s&time_from=%s&time_range_field=create_time&time_to=%s&timestamp=%s" %(self.access_token,self.shopee_partner_id,self.shopee_id,sign,data_inicio,data_fim,timest)
        url = url_ini + path + path_cat
        response = requests.request("GET",url,headers=headers, data=payload, allow_redirects=False)
        od_list = response.json()
        for od in od_list['response']['order_list']:
            order_sn = str(od['order_sn'])
            sale_exists = self.env['sale.order'].search([
                ('name', '=', str(od['order_sn'])),
            ])
            if sale_exists:
                continue
            if od['order_status'] == "UNPAID" or od['order_status'] == "CANCELLED":
                # print("PEDIDO CANCELADO OU NAO PAGO")
                continue
            if od['order_status'] == "PROCESSED":
                # print("PEDIDO JÁ ENVIADO")
                continue
            # PARTE QUE TRAS AS FATURAS CRIADAS E AS RESPECTIVAS INFORMACOES
            if od['order_status'] == "READY_TO_SHIP":
                path = "/api/v2/order/get_order_detail"
                tmp_base_string = "%s%s%s%s%s" % (self.shopee_partner_id, path, timest, self.access_token, self.shopee_id)
                base_string = tmp_base_string.encode()
                sign = hmac.new(self.shopee_partner_key.encode(), base_string, hashlib.sha256).hexdigest()
                optional = "total_amount,buyer_user_id,buyer_username,recipient_address,buyer_cpf_id,item_list"
                path_cat = (
                    f"?access_token={self.access_token}"
                    f"&order_sn_list={order_sn}"
                    f"&partner_id={self.shopee_partner_id}"
                    f"&response_optional_fields={optional}"
                    f"&shop_id={self.shopee_id}"
                    f"&sign={sign}"
                    f"&timestamp={timest}"
                )

                url = url_ini + path + path_cat

                response = requests.get(url)
                od_detail = response.json()
                order_name = ''
                prd_id = ''
                prd_qtd = ''
                prd_price = ''
                for z in od_detail['response']['order_list']:
                    order_line = []
                    for key, value in z.items():
                        if key == "item_list":
                            # print("ITEMS : ----------------------")
                            for itens in z["item_list"]:
                                for key, value in itens.items():
                                    # print(f"---------------ITEM : {key}--{value}")
                                    prd_sku = itens['item_sku']
                                    prd_id = itens['item_id']
                                    prd_qtd = itens['model_quantity_purchased']
                                    prd_price = itens['model_original_price']
                                    prd_name = itens['item_name']
                                    if itens['model_sku'] != "":
                                        prd_sku = itens['model_sku']
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
                                    'product_uom': prod.uom_id.id,
                                    'price_unit': prd_price,
                                    'name': prd_name,
                                }
                                order_line.append((0, 0,vals_line))
                        elif key == "recipient_address":
                            # print("Endereço : ===========================================")
                            for key, value in z["recipient_address"].items():
                                # print(f"ENDERECO : {key}-{value}")
                                if key == "name":
                                    name_buyer = value
                                if key == "city":
                                    city_buyer = value
                                if key == "full_address":
                                    street = value
                                    st_n = value
                                    street_n = st_n[st_n.find(",")+2:]
                        else:
                            # print(f"{key}--{value}")
                            order_name = str(z['order_sn'])
                            id_buyer = str(z['buyer_user_id'])
                            cpf_b = str(z['buyer_cpf_id'])
                            if len(cpf_b) < 11:
                                cpf_b = cpf_b.zfill(11)
                            cpf = '{}.{}.{}-{}'.format(cpf_b[:3], cpf_b[3:6], cpf_b[6:9], cpf_b[9:])
                    # print("PEDIDO CRIADO")
                    pr = self.env["res.partner"].search([
                        ('cnpj_cpf', '=', cpf),
                    ])
                    tag_pr = self.env['res.partner.category'].search([
                        ('name', '=', "Shopee"),
                    ])
                    state = self.env['res.country.state'].search([('name', '=', z['recipient_address']['state'])], limit=1)
                    if state.code == 'SP':
                        venda_final = self.env['account.fiscal.position'].search([
                            ('name', '=', 'Venda Consumidor Final - SP'),
                        ])
                    if state.code != 'SP':
                        venda_final = self.env['account.fiscal.position'].search([
                            ('name', '=', 'Venda Consumidor Final - Outros Estados'),
                        ])
                    cty = self.env['res.city'].search([
                        ('name', '=', city_buyer),
                        ('state_id', '=', state.id)
                    ])
                    if not pr:
                        vals_pr = {
                            'name': name_buyer,
                            'legal_name': name_buyer,
                            'cnpj_cpf': cpf,
                            'ref': id_buyer,
                            'street_name':  street[:street.find(",")],
                            'street_number': street_n[:street_n.find(",")],
                            'district': z['recipient_address']['district'],
                            'city_id': cty.id,
                            'state_id': state.id,
                            'zip': z['recipient_address']['zipcode'],
                            'category_id': [(6, 0, tag_pr.ids)],
                            'ind_final': '1',
                            'property_account_position_id': venda_final.id,
                            # 'is_customer': True,
                        }
                        pr = self.env['res.partner'].create(vals_pr)
                        if pr.cnpj_cpf:
                            pr._onchange_cnpj_cpf()
                    tag = self.env['crm.tag'].search([
                        ('name', '=', "Shopee"),
                    ])
                    vals={
                        "name": order_name,
                        "partner_id": pr.id,
                        "tag_ids": [(6, 0, tag.ids)],
                    }
                    
                    sale = self.env['sale.order'].create(vals)
                    sale.onchange_partner_id()
                    if len(order_line):
                        sale['order_line'] = order_line
                        for line in sale.order_line:
                            # preco unitario alterado no onchange
                            prd_price = line.price_unit
                            prd_name = line.name
                            line._onchange_product_id_fiscal()
                            line.write(
                                {'price_unit': prd_price,'name': prd_name,}
                            )
        return True

    def action_envia_xml_shopee(self):
        lj = self.search([('id', '=', 2 )])  # Ajuste o filtro conforme necessário
        for loja in lj:
            shopee = self.env['res.users'].search([
                ('name', '=', "Shopee"),
            ], limit=1)
            move_id = self.env['account.move'].search([
                ('state', '=', 'posted'),
                ('document_type_id', '=', 31),
                ('invoice_user_id', '=', shopee.id),
                ('create_date', '>=', (datetime.now() - timedelta(hours=7))),
                ('ref', '=', ''),
                ('fiscal_document_id.state', '=', 'autorizada'),
            ])
            if not move_id:
                print("Fatura não encontrada.")
                return True
            for mv in move_id:
                loja.envia_xml_shopee(mv)

    def envia_xml_shopee(self, move_id):
        if self.shop_real == True:
            url_ini = "https://openplatform.shopee.com.br"
        if self.shop_real == False:
            url_ini = "https://partner.test-stable.shopeemobile.com"
        if self.expire_date_token and self.expire_date_token < datetime.now():
            self.action_gera_acess_token()
            # print("TOKEN GERADO")
        path = "/api/v2/order/upload_invoice_doc"
        timestamp = int(time.time())
        access_token = self.access_token.strip()
        # Gera assinatura
        string_to_sign = f"{self.shopee_partner_id}{path}{timestamp}{access_token}{self.shopee_id}"
        sign = hmac.new(self.shopee_partner_key.encode(), string_to_sign.encode(), hashlib.sha256).hexdigest()
        file_path = tempfile.gettempdir()+'/' + move_id.fiscal_document_id.authorization_file_id.name
        data = base64.decodebytes(move_id.fiscal_document_id.authorization_file_id.datas)
        f = open(file_path,'wb')
        f.write(data)
        f.close()
        # Caminho do arquivo
        name_order = move_id.invoice_origin
        url = (
            f"{url_ini}{path}"
            f"?access_token={access_token}"
            f"&partner_id={self.shopee_partner_id}"
            f"&shop_id={self.shopee_id}"
            f"&sign={sign}"
            f"&timestamp={timestamp}"
        )
        # Parâmetros obrigatórios
        payload = {
            "order_sn": name_order,
            "file_type": 4
        }
        # Arquivo XML com tipo MIME correto
        files = {
            'file': (file_path.split('/')[-1], open(file_path, 'rb'), 'application/xml')
        }
        # Envia POST
        response = requests.post(url, data=payload, files=files)
        print("Status code:", response.status_code)
        print("Response:", response.text)
        if response.status_code == 200 and response.json().get('message') == '':
            print("XML enviado com sucesso.")
            move_id.ref = "XML enviado para Shopee"
        else:
            print("Erro ao enviar XML:", response.text)

