# -*- coding: utf-8 -*-
from odoo import api, fields, models

from datetime import datetime, date, timedelta
from dateutil import parser
import time
import json
import requests
import urllib3


class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def create(self, values):
        values['amount_return'] = values['amount_total']
        #import pudb;pu.db
        res = super(PosOrder, self).create(values)
        # atualiza estoque
        for item in res.lines:
            if not item.product_id.item_id:
                continue
            stock = item.product_id.product_tmpl_id.qty_available
            estoque = item.product_id.online_estoque
            # tratar estoque real e estoque informado online
            if not estoque:
                estoque = stock
            elif estoque >= stock:
                estoque = stock
            cod_barra = item.product_id.barcode
            codigo = item.product_id.default_code
            estoque_loja = self.estoque_loja(
            item.product_id.item_id, item.product_id.variant_id)
            #import pudb;pu.db
            if int(estoque) < estoque_loja:
                self.atualiza_estoque_loja(
                    item.product_id.item_id, 
                    item.product_id.variant_id, estoque)

        return res

    def nuvem_header(self):
        headers = {
                 'Content-Type': 'application/json; charset=utf-8',
                 'User-Agent': 'Awesome app (awesome@app.com)',
                 'Authentication': '%s' %(self.env.user.company_id.nuvem_shop_authentication) 
        }
        return headers
        
    def nuvem_url(self):
        url =  '%s%s/products/'  %(
                  self.env.user.company_id.nuvem_shop_link, 
                  self.env.user.company_id.nuvem_shop_id)
        return url

    def verifica_novo_cadastro(self):
        #import pudb;pu.db
        ultimo_prod = self.env['product.product'].search([
            ('item_id','!=', False),
            ], order='item_id desc', limit=1)
        http = urllib3.PoolManager()
        link = self.nuvem_url() + '123'
        if not ultimo_prod:
            #primeira importacao, faco dos 50 primeiros
            link = self.nuvem_url() + '?page=1&per_page=50'
        else:
            link = '%s?since_id=%s&per_page=100' %(
                self.nuvem_url(),
                str(ultimo_prod.item_id))
        r = requests.get(link, headers=self.nuvem_header())
        if r.status_code == 200:
            conta = 0
            for x in r.json():
                conta += 1
                if not x['variants']:
                    continue
                for z in x['variants']:
                    if z['sku']:
                        print ('Prod.: %s' %(x['name']))
                        print ('ID %s, SKU: %s' %(str(z['id']), z['sku']))
                        # atualizo o cadastro do produto no Odoo
                        prod = 0
                        if z['barcode']:
                            prod = self.env['product.product'].search([
                                ('barcode','=', z['barcode']),
                                ('item_id','=', False),])
                        if not prod:
                            prod = self.env['product.product'].search([
                                ('default_code','=', z['sku']),
                                ('item_id','=', False),])
                        if prod:
                            prod.write({'item_id': x['id'],
                                'variant_id': z['id']})

    def estoque_loja(self, cod_item, cod_variant):
        # consulta estoque Nuvemshop
        #import pudb;pu.db
        link = '%s%s/variants/%s' %(
                self.nuvem_url(),
                str(cod_item),str(cod_variant))
        r = requests.get(link, headers=self.nuvem_header())
        estoque = 0
        if r.status_code == 200:
            x = r.json()
            if x['stock']:
                estoque = x['stock']
        return estoque

    def atualiza_estoque_loja(self, id_item, id_variant, estoque):
        # atualiza o estoque na Nuvemshop
        #import pudb;pu.db
        prod = """{"id": %s, "stock":  %s, "product_id": %s}""" %(
            id_variant, str(int(estoque)), id_item)
        link = '%s%s/variants/%s' %(  
                self.nuvem_url(),
                str(id_item),str(id_variant))
        r = requests.put(link, headers=self.nuvem_header(), data=prod)
        if r.status_code == 200:
            return True
        return False

    @api.model
    def cron_atualiza_nuvemshop(self):
        # ---------------------------------------------------------------------------
        # este cron atualiza o estoque na nuvemshop quando 
        # ocorre uma venda
        # ---------------------------------------------------------------------------
        # Pega os itens dos ultimos 10 pedidos vendidos
        # pega o estoque atual de cada item
        # procura o estoque na nuvemshop
        # se maior q o estoque atual entao tem q diminuir
        #import pudb;pu.db
        data_ant = '%s-%s-%s 01:00:00' %(
            fields.date.today().year, 
            fields.date.today().month,
            fields.date.today().day-3)
        #data_ant = '2021-04-20 08:00:00'
        pedidos = self.env['pos.order'].search([
            ('create_date','>', data_ant),
            ], order='id desc', limit=10)
        #self.verifica_novo_cadastro()   #  coloquei isso pra acertar os cadastros q existiam
        for ped in pedidos:
            for item in ped.lines:
                 if not item.product_id.item_id:
                     continue                 
                 stock = item.product_id.product_tmpl_id.qty_available
                 # 08/11/2022 vai colocar o estoque real la
                 # nao preciso deste campo abaixo
                 #estoque = item.product_id.online_estoque
                 # tratar estoque real e estoque informado online
                 #if not estoque:
                 estoque = stock
                 #elif estoque >= stock:
                 #    estoque = stock
                 cod_barra = item.product_id.barcode
                 codigo = item.product_id.default_code
                 #estoque_loja = self.estoque_loja(item.product_id.item_id, item.product_id.variant_id)
                 #import pudb;pu.db
                 #if int(estoque) < estoque_loja:
                 self.atualiza_estoque_loja(item.product_id.item_id, item.product_id.variant_id, estoque)
        return True
