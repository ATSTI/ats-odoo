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
        # Mostrar IDs dos pedidos
        # Vazio por enquanto
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
            # PEGANDO O ENDEREÇO DE ENTREGA
            shipping_id = order["shipping"]["id"]
            url = f'https://api.mercadolibre.com/shipments/{shipping_id}'
            ship_address = requests.get(url, headers=headers)
            if ship_address.status_code == 200:
                data = ship_address.json()
                address = data.get('receiver_address', {})
                bairro = address.get('neighborhood')
                rua = address.get('street_name')
                numero = address.get('street_number')
                city_buyer = address.get('city', {}).get('name')
                state_buyer = address.get('state', {}).get('name')
                zip_buyer = address.get('zip_code')
            name_buyer = f"{first_name} {order.get('buyer', {}).get('last_name')}"
            order_line = []
            order_name = order['id']
            url = f'https://api.mercadolibre.com/orders/{order_name}/billing_info'
            hd = {
                'Authorization': f'Bearer APP_USR-7103092091034476-051909-282eaf0539a8fbfc671e9117e8b5cb87-540196762',
                'x-version': '2'
            }
            address_buyer = requests.get(url, headers=hd)
            cpf_buyer = address_buyer.json()['buyer']['billing_info']['identification']['number']
            order_amount = order['total_amount']
            order_date = order['date_created']
            for itens in order['order_items']:
                # print("ITEMS : ----------------------") 
                id_item = itens['item']['id']
                prd_name = itens['item']['title']
                categ_item = itens['item']['category_id']
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
            uom = self.env['uom.uom'].search([
                ('id', '=', 1),
            ])
            vals_line = {
                'product_id': prod.id,
                'product_uom_qty': prd_qtd,
                'product_uom': uom.id,
                'price_unit': prd_price,
                'name': prd_name,
            }
            order_line.append((0, 0,vals_line))
            buyer_id = order['buyer']['id']
            pr = self.env["res.partner"].search([
                ('cnpj_cpf', '=' , cpf_buyer) or ('ref', '=', buyer_id),
            ])
            tag_pr = self.env['res.partner.category'].search([
                ('name', '=', "Mercado Livre"),
            ])
            state = self.env['res.country.state'].search([('name', '=', state_buyer)], limit=1)
            cty = self.env['res.city'].search([
                ('name', '=', city_buyer),
                ('state_id', '=', state.id)
            ])
            if not pr:
                vals_pr = {
                    'name': name_buyer,
                    'legal_name': name_buyer,
                    'cnpj_cpf': cpf_buyer,
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
                }
                pr = self.env['res.partner'].create(vals_pr)
                if pr.cnpj_cpf:
                    pr._onchange_cnpj_cpf()
            tag = self.env['crm.tag'].search([
                ('name', '=', "Mercado Livre"),
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