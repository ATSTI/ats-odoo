# -*- encoding: utf-8 -*-
import requests
import urllib3
import json
from odoo import models, _, api

class StockPicking(models.Model): 
    _inherit = "stock.picking"

    def nuvem_header(self):
        headers = {
                 'Content-Type': 'application/json; charset=utf-8',
                 'User-Agent': 'Awesome app (awesome@app.com)',
                 'Authentication': '%s' %(self.env.user.company_id.nuvem_shop_authentication) 
        }
        return headers
        
    def nuvem_url(self):
        url =  '%s%s/products'  %(
                  self.env.user.company_id.nuvem_shop_link, 
                  self.env.user.company_id.nuvem_shop_id)
        return url

    def atualiza_estoque(self, product, stock):
        http = urllib3.PoolManager()
        link = '%s/%s/variants/stock' %(
            self.nuvem_url(),
            str(product.item_id))
        values = {"action" : "replace", "value" : int(stock), "id" : product.variant_id,}

        headers = {
                 'Content-Type': 'application/json; charset=utf-8',
                 'User-Agent': 'Awesome app (awesome@app.com)',
                 'Authentication': '%s' %(self.company_id.nuvem_shop_authentication) 
        }
        r = requests.post(link, headers=headers, data=json.dumps(values))
        if r.status_code == 200:
            return True

    @api.multi
    def action_done(self):
        result = super(StockPicking, self).action_done()
        for pick in self:
            for item in pick.move_line_ids_without_package:
                try:
                    if item.product_id.item_id:
                        estoque = 0
                        if item.product_id.qty_available > 0:
                            estoque = item.product_id.qty_available
                        self.atualiza_estoque(item.product_id, estoque)
                except:
                    return False
        return result


class Inventory(models.Model): 
    _inherit = "stock.inventory"


    """
       Qdo tem algum movimento no Inventario , tbem atualiza a loja
    """
    def nuvem_header(self):
        headers = {
                 'Content-Type': 'application/json; charset=utf-8',
                 'User-Agent': 'Awesome app (awesome@app.com)',
                 'Authentication': '%s' %(self.env.user.company_id.nuvem_shop_authentication) 
        }
        return headers
        
    def nuvem_url(self):
        url =  '%s%s/products'  %(
                  self.env.user.company_id.nuvem_shop_link, 
                  self.env.user.company_id.nuvem_shop_id)
        return url

    def atualiza_estoque(self, product, stock):
        http = urllib3.PoolManager()
        link = '%s/%s/variants/stock' %(
            self.nuvem_url(),
            str(product.item_id))
        values = {"action" : "replace", "value" : int(stock), "id" : product.variant_id,}

        headers = {
                 'Content-Type': 'application/json; charset=utf-8',
                 'User-Agent': 'Awesome app (awesome@app.com)',
                 'Authentication': '%s' %(self.company_id.nuvem_shop_authentication) 
        }
        r = requests.post(link, headers=headers, data=json.dumps(values))
        if r.status_code == 200:
            return True

    @api.multi
    def _action_done(self):
        result = super(Inventory, self)._action_done()
        for invent in self:
            for item in invent.line_ids:
                try:
                    if item.product_id.item_id:
                        estoque = 0
                        if item.product_id.qty_available > 0:
                            estoque = item.product_id.qty_available
                        self.atualiza_estoque(item.product_id, estoque)
                except:
                    return False
        return result