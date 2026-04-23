# -*- coding:utf-8 -*-

from odoo import models, _


import requests as rq
import json
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = "product.template"

    def enviando_new_standard_price(self):
        config_db = self.env['ir.config_parameter'].sudo().get_param('product_template.db')
        config_user = self.env['ir.config_parameter'].sudo().get_param('product_template.user')
        config_passwd = self.env['ir.config_parameter'].sudo().get_param('product_template.passwd')
        config_url = self.env['ir.config_parameter'].sudo().get_param('product_template.url')
        hoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        audit = self.env['auditlog.log'].sudo().search([
            ('create_date', '>=', hoje.strftime('%Y-%m-%d %H:%M:%S')),
            ('model_id', '=', 'product.template'),
        ], order='create_date')
        dados = {}
        session_id = self.get_session(config_url, config_user, config_passwd, config_db)
        for pr in audit:
            for line in pr.line_ids:
                if line.field_name == 'list_price':
                    dados['list_price'] = line.new_value,
                    prod = self.env['product.template'].sudo().browse([pr.res_id])
                    dados['default_code'] = prod.default_code
                    envio = self.enviando_arquivo(dados, session_id, config_db, config_user, config_passwd, config_url)
                    # if envio.json()['result']['product_id'] and  envio.json()['result']['success'] == True:
                    #     pr.unlink()
                    # else:
                    #     _logger.error('Erro ao enviar o preço do produto {} para o Odoo. Resposta: {}'.format(prod.default_code, envio.text))
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
        url = 'http://%s/web/session/authenticate' % (url)
        response = rq.post(url, json=data, headers=headers)
        session_id = response.cookies.get('session_id')
        return session_id

    def enviando_arquivo(self, dados, session_id, db, user, password, url):
        base_url = '%s/atualiza_preco' %(url)
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
        return rq.post("http://{}".format(base_url), 
        json={
            "jsonrpc": "2.0",
            "method": "call",
            "params": dados
        },
        headers=json_headers, cookies=cookies)
