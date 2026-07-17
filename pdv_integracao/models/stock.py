# -*- coding:utf-8 -*-

from odoo import models, _


import requests as rq
import json



class StockPicking(models.Model):
    _inherit = "stock.picking"

    def enviando_picking(self):
        config_db = self.env['ir.config_parameter'].sudo().get_param('stock_picking.db')
        config_user = self.env['ir.config_parameter'].sudo().get_param('stock_picking.user')
        config_passwd = self.env['ir.config_parameter'].sudo().get_param('stock_picking.passwd')
        config_url = self.env['ir.config_parameter'].sudo().get_param('stock_picking.url')
        # buscar picking que ainda não foram enviados
        if self.model_name == 'stock.picking' and self:
            stq_origem = self
        else:
            stq_origem = self.env['stock.picking'].search([('location_dest_id', '=', 43), ('state', '=', 'done'),], order="id desc", limit=5)
        session_id = self.get_session(config_url, config_user, config_passwd, config_db)
        for st in stq_origem:
            for line in st.move_ids_without_package:
                vals = {
                    'default_code': line.product_id.default_code,
                    'quantity': line.product_uom_qty,
                    'price': line.product_id.lst_price,
                    'product': line.product_id.read()
                }
                itens = json.dumps(vals, default=str)
                envio = self.enviando_arquivo(itens, session_id, config_db, config_user, config_passwd, config_url)
        return True    

    def get_session(self, url, username, password, db):
        headers = {'Content-Type': 'application/json'}
        data = {
            'jsonrpc': '2.0',
            'method': 'call',
            'params': {
                'db': db,
                'login': username,
                'password': password
            },
            'id': 1
        }
        url = 'https://%s/web/session/authenticate' % (url)
        response = rq.post(url, json=data, headers=headers)
        session_id = response.cookies.get('session_id')
        return session_id

    def enviando_arquivo(self, dados, session_id, db, user, password, url):
        base_url = '%s/enviandoestoque' %(url)
        json_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            }
        cookies = {
            "login": user,
            "password": password,
            'session_id':session_id
        }
        #json_data = json.dumps(dados)
        return rq.post("https://{}".format(base_url), data=dados, headers=json_headers, cookies=cookies)
