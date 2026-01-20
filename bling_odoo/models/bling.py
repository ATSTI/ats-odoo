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
import re

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
        else:
            raise UserError("Erro ao buscar as notas fiscais;/nDetalhes: %s" % response.text)

    def criar_pedido_bling(self, nf):
        numero_pedido = nf.get('numero')
        pedido_inf = self.busca_pedido(numero_pedido)
        parceiro = nf['contato']
        Partner = self.env['res.partner']
        cnpj_cpf = parceiro['numeroDocumento']
        cnpj_cpf = re.sub(r'\D', '', cnpj_cpf)
        if len(cnpj_cpf) == 11:
            parceiro_tipo = 'person'
            cnpj_cpf = self.formatar_cpf(cnpj_cpf)
        elif len(cnpj_cpf) == 14:
            parceiro_tipo = 'company'
            cnpj_cpf = self.formatar_cnpj(cnpj_cpf)
        else:
            raise ValueError("Documento inválido: não é CPF nem CNPJ")
        pr = Partner.search([
            ('name', 'ilike', parceiro['nome']),
            ('company_type', '=', parceiro_tipo),
            ('cnpj_cpf', '=', cnpj_cpf)
        ], limit=1)
        if not pr:
            pr_vals = {
                'name': parceiro['nome'],
                'company_type': parceiro_tipo,
                'cnpj_cpf': cnpj_cpf,
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
        order_line = []
        for item in pedido_inf['data']['itens']:
            prod_id = item['produto']['id']
            prd = self.busca_produto(prod_id)
            line_vals = {
                'order_id': so.id,
                'product_id': prd.id,
                'product_uom_qty': float(item.get('quantidade', 1.0)),
                'price_unit': float(item.get('valor', 0.0)),
            }
            order_line.append((0, 0, line_vals))
        so.write({'order_line': order_line})
        so.action_confirm()
        for line in so.order_line:
            line.product_id_change()
            availability = line._onchange_product_id_check_availability()
            if availability.get('warning'):
                so.message_post(
                    subject="Aviso de Estoque",
                    body="Você planeja vender %s %s de %s mas só tem %s disponível em estoque. <br/> Cancelando as outras etapas" % (line.product_uom_qty, line.product_uom.name, line.product_id.name, line.product_id.qty_available),
                )
                return True
        for picking in so.picking_ids:
            if picking.state == "cancel":
                continue
            picking.action_assign()
            picking.button_validate()
            if picking.state == 'assigned':
                picking.action_done()
        so.action_invoice_create()
        # nat_operacao = nf.get('naturezaOperacao')
        return True

    def busca_pedido(self, pedido_id):
        url = "https://developer.bling.com.br/api/bling/pedidos/vendas/%s" % pedido_id
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
        
    def busca_produto(self, produto_id):
        url = "https://api.bling.com.br/Api/v3/produtos/%s" % producto_id

        headers = {
            "accept": "application/json",
            "Authorization": "Bearer %s" % self.access_token
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            res = response.json()
            prd = res['data']
            ProductProduct = self.env['product.product']
            prod = ProductProduct.search([
                '|',
                ('name', '=', prd['nome']),
                ('default_code', '=', prd['codigo'])
            ], limit=1)
            if prod:
                return prod
            else:
                prod_vals = {
                    'name': prd.get('nome'),
                    'default_code': prd.get('codigo'),
                    'list_price': float(prd.get('preco', 0.0)),
                    'type': 'product',
                }
                return ProductProduct.create(prod_vals)

    def formatar_cpf(self, cpf):
        cpf = re.sub(r'\D', '', cpf)  # remove tudo que não é número
        return "%s.%s.%s-%s" % (cpf[:3], cpf[3:6], cpf[6:9], cpf[9:])

    def formatar_cnpj(self,cnpj):
        cnpj = re.sub(r'\D', '', cnpj)
        return "%s.%s.%s/%s-%s" % (cnpj[:2], cnpj[2:5], cnpj[5:8], cnpj[8:12], cnpj[12:])