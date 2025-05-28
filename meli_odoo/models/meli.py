# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import requests
import json
import time
import hmac
import hashlib

class MeliConfig(models.Model):
    _name = 'meli.config'
    _description = "Mercado Livre Config"

    name = fields.Char('Nome da Loja', required=True)
    meli_id = fields.Char('Client ID', required=True)
    access_token = fields.Char('Access Token', readonly=True)
    expire_date_token = fields.Datetime('Expire Date Token', readonly=True)
    refresh_token = fields.Char('Refresh Token')
    refresh_token_security = fields.Char('Refresh Token security', invisible=True, readonly=True)
    user_id = fields.Char('Usuario ID') #TODO PENSAR NO CASO DE EXISTIREM MAIS DE UM USUARIO
    client_meli_key = fields.Char('Client Secret Key', required=True)

    def action_gera_acess_token(self):
        headers = {
            'accept': 'application/json',
            'content-type': 'application/x-www-form-urlencoded',
        }
        url = f"https://api.mercadolibre.com/oauth/token?grant_type=authorization_code&client_id={self.meli_id}&client_secret={self.client_meli_key}&code={self.refresh_token}&redirect_uri=https://sindicato-teste.atsti.com.br"
        data = {
            'grant_type': 'refresh_token',
            'client_id': self.meli_id,
            'client_secret': self.client_meli_key,
            'refresh_token': self.refresh_token,
        }

        response = requests.post('https://api.mercadolibre.com/oauth/token', headers=headers, data=data)
        tk_new = response.json()
        self.access_token = tk_new['access_token']
        self.expire_date_token = datetime.now() + timedelta(seconds=tk_new['expires_in'])
        self.refresh_token = tk_new['refresh_token']
        self.refresh_token_security = tk_new['refresh_token']
        self.user_id = tk_new['user_id']

    def _inserir_linhas(self, order, pedido):
        order_line = []
        for itens in order['order_items']: 
            id_item = itens['item']['id']
            prd_name = itens['item']['title']
            categ_item = itens['item']['category_id']
            headers = {
                'Authorization': 'Bearer %s' % (self.access_token),
            }
            url = f'https://api.mercadolibre.com/categories/{categ_item}'
            response = requests.get(url, headers=headers)
            categ = response.json()
            categ = categ['name']
            sku_item = itens['item']['seller_sku']
            prd_price = itens['unit_price']
            prd_qtd = itens['quantity']
            if not sku_item:
                prod = self.env["product.product"].search([
                    ('default_code', '=', 999999),
                ])
                prd_name = f"[SEM SKU NO MELI] {prd_name}"
            else:
                prod = self.env["product.product"].search([
                    ('default_code', '=', sku_item),
                ])
            if not prod:
                prod = self.env["product.product"].search([
                    ('default_code', '=', 999999),
                ])
                prd_name = f"[{sku_item}] {prd_name}"
            else:
                prod.meli = True
                prod.meli_sku = sku_item
                prod.title_meli = prd_name
                prod.category_meli = categ
                prod.categ_meli_id = categ_item
                prod.meli_config_id = self.id
                prod.meli_item_id = id_item
            vals_line = {
                'product_id': prod.id,
                'product_uom_qty': prd_qtd,
                'product_uom': prod.uom_id.id,
                'price_unit': prd_price,
                'name': prd_name,
            }
            order_line.append((0, 0,vals_line))
            if len(order_line):
                pedido['order_line'] = order_line
                for line in pedido.order_line:
                    prd_price = line.price_unit
                    prd_name = line.name
                    if pedido.name == str(order['id']):
                        line.write(
                            {'price_unit': prd_price,'name': prd_name}
                        )
                    else:
                        order_id_meli = order['id']
                        line._onchange_product_id_fiscal()
                        line.write(
                            {'price_unit': prd_price,'name': prd_name, 'order_id_meli': order_id_meli}
                        )
    
    def cron_execute_pega_faturas(self):
        lj = self.search([])
        for loja in lj:
            loja.action_pega_faturas_meli()
       
    def action_pega_faturas_meli(self):
        if self.expire_date_token and self.expire_date_token < datetime.now():
            self.action_gera_acess_token()
            # print("TOKEN GERADO")
        headers = {
            'Authorization': 'Bearer %s' %(self.access_token),
        }
        hoje = str(datetime.today().date())
        url = f"https://api.mercadolibre.com/orders/search?seller={self.user_id}&order.date_created.from={hoje}T00:00:00Z&order.date_created.to={hoje}T23:59:59Z"
        response = requests.get(url, headers=headers)
        order_list = response.json()
        for orders in order_list.get("results", []):
            order_id = orders['id']
            sale_exists = self.env['sale.order'].search([
                ('name', '=', str(order_id)),
            ])
            if sale_exists:
                continue
            url = f'https://api.mercadolibre.com/orders/{order_id}'
            response = requests.get(url, headers=headers)
            order = response.json()
            first_name = order.get('buyer', {}).get('first_name')
            email = order.get('buyer', {}).get('email')
            shipping_id = order["shipping"]["id"]
            same_sale = self.env['sale.order'].search([
                ('origin', '=', shipping_id),
                ('state', 'in', ['draft']),
            ])
            if same_sale:
                sale_line_exist = False
                for ol in same_sale.order_line:
                    if ol.order_id_meli:
                        for y in ol.order_id_meli.split():
                            sale_line_exist = self.env['sale.order.line'].search([
                                ('order_id_meli', '=', y),
                            ])
                            if sale_line_exist:
                                sale_line_exist = True
                                break
                if sale_line_exist == False:
                    self._inserir_linhas(order, same_sale)
                    continue
                if sale_line_exist == True:
                    continue
            url = f'https://api.mercadolibre.com/shipments/{shipping_id}'
            ship_address = requests.get(url, headers=headers)
            if ship_address.status_code == 200:
                data = ship_address.json()
                ou1 = self.env["operating.unit"].search([
                        ('code', '=', 'OU1'),
                    ])
                full = ou1
                mf = self.env["operating.unit"].search([
                        ('code', '=', 'MF'),
                    ])
                if data.get('logistic_type') == 'fulfillment':
                    full = mf
                # print(f'Full: {full.name}')
                address = data.get('receiver_address', {})
                bairro = address.get('neighborhood')
                rua = address.get('street_name')
                numero = address.get('street_number')
                city_buyer = address.get('city', {}).get('name')
                state_buyer = address.get('state', {}).get('name')
                zip_buyer = address.get('zip_code')
            name_buyer = f"{first_name} {order.get('buyer', {}).get('last_name')}"
            order_name = order['id']
            url = f'https://api.mercadolibre.com/orders/{order_name}/billing_info'
            hd = {
                'Authorization': f'Bearer {self.access_token}',
                'x-version': '2'
            }
            address_buyer = requests.get(url, headers=hd)
            cpfj_buyer = address_buyer.json()['buyer']['billing_info']['identification']['number']
            if len(cpfj_buyer) == 11:
                cpfj_buyer = cpfj_buyer.zfill(11)
                cpfj = '{}.{}.{}-{}'.format(cpfj_buyer[:3], cpfj_buyer[3:6], cpfj_buyer[6:9], cpfj_buyer[9:])
            if len(cpfj_buyer) == 14:
                cpfj_buyer = cpfj_buyer.zfill(14)
                cpfj = '{}.{}.{}/{}-{}'.format(cpfj_buyer[:2], cpfj_buyer[2:5], cpfj_buyer[5:8], cpfj_buyer[8:12], cpfj_buyer[12:])    
            order_amount = order['total_amount']
            order_date = order['date_created']
            buyer_id = order['buyer']['id']
            pr = self.env["res.partner"].search([
                ('cnpj_cpf', '=' , cpfj) or ('ref', '=', buyer_id),
            ])
            if not pr:
                tag_pr = self.env['res.partner.category'].search([
                    ('name', '=', "Mercado Livre"),
                ])
                state = self.env['res.country.state'].search([
                    ('name', '=', state_buyer), 
                    ('country_id', '=', 32)
                ], limit=1)
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
                vals_pr = {
                    'name': name_buyer,
                    'legal_name': name_buyer,
                    'cnpj_cpf': cpfj,
                    'ref': buyer_id,
                    'street_name':  rua,
                    'street_number': numero,
                    'district': bairro['name'],
                    'city_id': cty.id,
                    'state_id': state.id,
                    'zip': zip_buyer,
                    'category_id': [(6, 0, tag_pr.ids)],
                    'ind_final': '1',
                    'is_customer': True,
                    'property_account_position_id': venda_final.id,
                }
                pr = self.env['res.partner'].create(vals_pr)
                if pr.cnpj_cpf:
                    pr._onchange_cnpj_cpf()
            tag = self.env['crm.tag'].search([
                ('name', '=', "Mercado Livre"),
            ])
            team = self.env['crm.team'].search([
                ('operating_unit_id','=', full.id),
            ], limit=1)
            wh = self.env["stock.warehouse"].search(
                [("operating_unit_id", "=", full.id)]
            )
            vals={
                "name": order_name,
                "partner_id": pr.id,
                "tag_ids": [(6, 0, tag.ids)],
                "origin": shipping_id,
                "fiscal_operation_id": 1,
            }
            sale = self.env['sale.order'].create(vals)
            if full.id == mf.id:
                sale.write({"operating_unit_id": full.id, "team_id": team.id, "warehouse_id": wh.id, "fiscal_operation_id": False})
                sale.onchange_team_id()
                sale.onchange_operating_unit_id()
                sale._check_wh_operating_unit()
            else:
                sale.onchange_partner_id()
            self._inserir_linhas(order, sale)   