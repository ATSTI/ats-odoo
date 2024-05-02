
# -*- coding: utf-8 -*-
#
#    Copyright © 2019–; Brasil; IT Brasil; Todos os direitos reservados
#    Copyright © 2019–; Brazil; IT Brasil; All rights reserved
#
from datetime import datetime
import logging
from datetime import timedelta
from unidecode import unidecode
import json
import re
from odoo import http
from odoo.http import request
from math import floor
logger = logging.getLogger(__name__)
import werkzeug
import werkzeug.exceptions
import werkzeug.utils
import werkzeug.wrappers
import werkzeug.wsgi
from werkzeug.urls import url_decode, iri_to_uri



class IntegracaoPdv(http.Controller):

    @http.route('/nfe', type='json', auth="user", csrf=False)
    def website_nfe(self, **kwargs):
        data = request.params
        num_nota = len(data)
        order = http.request.env['sale.order']
        cliente = http.request.env['res.partner']

        # crio uma lista com CNPJs unicos
        lista_cnpj = set()
        while num_nota > 0:
            # print (f" ---- Nota {num_nota} -----------")
            chave = str(num_nota)
            cnpj_emitente = data[chave]['empresa_cnpj']
            data_nota = data[chave]['nota_data']
            cnpj = re.sub('[^0-9]', '', cnpj_emitente)
            cnpj = '%s.%s.%s/%s-%s' %(cnpj[:2],cnpj[2:5],cnpj[5:8],cnpj[8:12],cnpj[12:14])
            lista_cnpj.add(cnpj)

        # criar lista do financeiro
        lista_financeiro = set()
        for lista in lista_cnpj:
            cli_ids = cliente.sudo().search([('cnpj_cpf', '=', lista),])
            # se cliente tem financeiro, cobranca e dele
            if cli_ids.financeiro:
                lista_financeiro.add(cli_ids.id)

        # criando ou alterando pedidos
        for fin in lista_financeiro:
            # procura se existe um pedido de venda, deste financeiro
            data_pedido = datetime.strptime(data_nota, "%Y-%m-%d %H:%M:%S")
            data_pedido = data_pedido + timedelta(months=1)
            data_pedido = data_pedido.replace(day=1, hour=0, minute=59, second=0, microsecond=0)

            order_id = order.sudo().search([
                ('partner_id', '=', fin),
                ('date_order', '=', data_pedido),
                ('state', '=', 'draft'),
                ], limit=1)
            if not order_id:
                # crio o pedido
                vals = {
                    'partner_id': fin,
                    'date_order': data_pedido,
                }
                order_id = order.sudo().create(vals)
                # inserir uma linha por CNPJ
            else:              
                # verificar se cnpj ja inserido na linha
                order_line = []
                for line in order_id:
                    if lista in line.name:
                        continue
                    else:
                        # insere
                        vals_line = {
                            'name': lista,
                            'product_id': 60,
                            'qty': 1,
                            'price_unit': 1,
                        }
                        order_id.sudo().write(vals_line)
                        order_line.append((0, 0,vals_line))
                order_id['lines'] = order_line


            # for key in data[chave]:
                # print(key, data[chave][key])
            # num_nota -= 1

            # prod_ids = http.request.env['product.product'].sudo().search([
            #     ('product_tmpl_id','in',list(prd_ids))])

    