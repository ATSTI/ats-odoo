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

class BlingConfig(models.Model):
    _name = 'bling.config'
    _description = "Bling Config"

    name = fields.Char('Nome da Loja', required=True)
    bling_id = fields.Char('Bling ID', required=True)
    access_token = fields.Char('Access Token', readonly=True)
    expire_date_token = fields.Datetime('Expire Date Token', readonly=True)
    refresh_token = fields.Char('Refresh Token', required=True)
    refresh_token_security = fields.Char('Refresh Token security', invisible=True, readonly=True)
    client_id = fields.Char('Client ID', required=True)
    client_secret = fields.Char('Client Secret', required=True)
    data_nota_inicial = fields.Datetime('Data Nota Inicial', required=True)
    data_nota_final = fields.Datetime('Data Nota Final', required=True)

    def action_gerar_access_token(self):
        url = "https://bling.com.br/Api/v3/oauth/token"
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token
        }
        response = requests.post(
            url,
            data=data,
            auth=(self.client_id, self.client_secret),
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "accept": "application/json"
            }
        )
        res = response.json()
        if response.status_code == 200:
            expire_in = res['expires_in']
            validade = datetime.now() + timedelta(seconds=expire_in)
            self.expire_date_token = validade
            self.access_token = res['access_token']
            self.refresh_token = res['refresh_token']
            self.refresh_token_security = res['refresh_token']
        else:
            raise UserError("Erro ao gerar o access token;/nDetalhes: %s" % res)
        
    def cron_execute_pega_faturas(self):
        lj = self.search([])
        for loja in lj:
            loja.action_pega_notas_bling()

    def action_pega_notas_bling(self):
        if self.expire_date_token and self.expire_date_token < datetime.now():
            self.action_gerar_access_token()
            # print("TOKEN GERADO")
        url = "https://developer.bling.com.br/api/bling/nfe"
        headers = {
            "accept": "application/json",
            "Authorization": "Bearer %s" % self.access_token
        }

        params = {
            "pagina": 1,
            "limite": 5,
            "numeroLoja": 0,
            "idTransportador": 0,
            "chaveAcesso": "",
            "numero": 0,
            "serie": 0,
            "situacao": 5,
            "tipo": 1,
            "dataEmissaoInicial": self.data_nota_inicial.strftime("%Y-%m-%d %H:%M:%S"),
            "dataEmissaoFinal": self.data_nota_final.strftime("%Y-%m-%d %H:%M:%S")
        }

        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=10
        )
        if response.status_code == 200:
            nf_list = response.json()
            for nf in nf_list['data']:
                self.criar_pedido_bling(nf)

    def criar_pedido_bling(self, nf):
        numero_pedido = nf.get('numero')
        pedido_inf = self.busca_pedido(numero_pedido)
        parceiro = nf['contato']
        if len(parceiro['numeroDocumento']) == 11:
            parceiro_tipo = 'person'
        else:
            parceiro_tipo = 'company'
        Partner = self.env['res.partner']
        pr = Partner.search([
            ('name', '=', parceiro['nome']), 
            ('company_type', '=', parceiro_tipo), 
            ('cnpj_cpf', '=', parceiro['numeroDocumento'])
        ], limit=1)
        if not pr:
            pr_vals = {
                'name': parceiro['nome'],
                'company_type': parceiro_tipo,
                'cnpj_cpf': parceiro['numeroDocumento'],
                'street': parceiro['endereco'].get('endereco', ''),
                'street2': parceiro['endereco'].get('complemento', ''),
                'city': parceiro['endereco'].get('municipio', ''),
                'state_id': self.env['res.country.state'].search([('code', '=', parceiro['endereco'].get('uf', ''))], limit=1).id,
                'zip': parceiro['endereco'].get('cep', ''),
                'phone': parceiro.get('telefone', ''),
                'email': parceiro.get('email', ''),
            }
            pr = Partner.create(pr_vals)
        SaleOrder = self.env['sale.order']
        vals={
                "name": self.env['ir.sequence'].next_by_code('sale.order'),
                "partner_id": pr.id,
            }
        so = SaleOrder.create(vals)
        so.onchange_partner_id()
        order_line = pedido_inf.get('itens', [])
        if len(order_line):
            so['order_line'] = order_line
            for line in so.order_line:
                # preco unitario alterado no onchange
                prd_price = line.price_unit
                prd_name = line.name
                line._onchange_product_id_fiscal()
                line.write(
                    {'price_unit': prd_price,'name': prd_name,}
                )
        nat_operacao = nf.get('naturezaOperacao')
        # BUSCANDO OU CRIANDO PARCEIRO, PRODUTOS E ADICIONANDO ITENS NO PEDIDO
        #TODO descobrir onde vai encaixar a natureza da operação, criação de fatura, teste para ver se o pedido vai criar corretamente
        return True
    
    def busca_pedido(self, pedido_id):
        url = f"https://developer.bling.com.br/api/bling/pedidos/vendas/{pedido_id}"
        headers = {
            "accept": "application/json",
            "Authorization": "Bearer ACCESS_TOKEN_AQUI"
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            res = response.json()
            for pedido in res['data']:
                return pedido
        return None

