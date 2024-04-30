
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
        for emp in data:
            cnpj = emp
        data_emp = json.loads(emp)
        cnpj = data_emp[0]['cnpj']                                                                                                   
        #data = request.jsonrequest
        #cnpj = re.sub('[^0-9]', '', data['params']['cnpj'])
        cnpj = re.sub('[^0-9]', '', cnpj)
        # TODO testar aqui se e a empresa mesmo
        cnpj = '%s.%s.%s/%s-%s' %(cnpj[:2],cnpj[2:5],cnpj[5:8],cnpj[8:12],cnpj[12:14])
        cliente = http.request.env['res.partner']
        cli_ids = cliente.sudo().search([('cnpj_cpf', '=', cnpj),])
        lista = []
        cliente = 'N'
        for partner_id in cli_ids:
            if partner_id.ref:
                cliente = partner_id.ref
        # TODO testar aqui se e a empresa mesmo
        hj = datetime.now()
        hj = hj - timedelta(days=20)
        hj = datetime.strftime(hj,'%Y-%m-%d %H:%M:%S')
        prod_tmpl = http.request.env['product.template'].sudo().search([
            ('write_date', '>=', hj),
            ('sale_ok', '=', True)])
        prod_ids = []
        prd_ids = set()
        for pr in prod_tmpl:
            prd_ids.add(pr.id)

        if len(prd_ids):
            prod_ids = http.request.env['product.product'].sudo().search([
                ('product_tmpl_id','in',list(prd_ids))])
        #print ('Qtde de Produtos %s\n' %(str(len(prod_ids))))
        lista = []
        for prd in prod_ids:
            prod = {}
            ncm = ''
            if prd.fiscal_classification_id:
                ncm = prd.fiscal_classification_id.code
                if ncm:
                    ncm = re.sub('[^0-9]', '', ncm)
            if ncm and len(ncm) > 8:
                ncm = '00000000'
            prod['codproduto'] = prd.id
            prod['unidademedida'] = prd.uom_id.name.strip()[:2]
            produto = prd.name.strip()
            produto = produto.replace("'"," ")
            produto = unidecode(produto)
            prod['produto'] = produto
            prod['valor_prazo'] = prd.list_price
            if prd.write_date > prd.product_tmpl_id.write_date:
                data_alt = prd.write_date
            else:
                data_alt = prd.product_tmpl_id.write_date
            data_alterado = data_alt + timedelta(hours=+3)
            prod['datacadastro'] = datetime.strftime(data_alterado,'%m/%d/%Y %H:%M:%S')
            if prd.default_code:
                codpro = prd.default_code.strip()
            else:
                codpro = str(prd.id)
            prod['codpro'] = codpro[:15]
            if prd.origin:
                prod['origem'] = prd.origin
            prod['ncm'] = ncm
            prod['usa'] = 'S'
            if prd.barcode and len(prd.barcode) < 14:
                prod['cod_barra'] = prd.barcode.strip()
            lista.append(prod)



        # Itens inativos
        prod_tmpl = http.request.env['product.template'].sudo().search([
            ('write_date', '>=', hj),
            ('sale_ok', '=', True),
            ('active' ,'=', False)])
        prd_ids = set()
        prod_ids = []
        for pr in prod_tmpl:
            prd_ids.add(pr.id)

        if prod_tmpl:
            prod_ids = http.request.env['product.product'].sudo().search([
                ('product_tmpl_id','in',list(prd_ids)),
                ('active','=', False)])       
        for prd in prod_ids:
            prod = {}
            prod['codproduto'] = prd.id
            data_alt = prd.write_date
            data_alterado = data_alt + timedelta(hours=+3)
            prod['datacadastro'] = datetime.strftime(data_alterado,'%m/%d/%Y %H:%M:%S')
            prod['usa'] = 'N'
            produto = prd.name.strip()
            produto = produto.replace("'"," ")
            produto = unidecode(produto)
            prod['produto'] = produto
            if prd.default_code:
                codpro = prd.default_code.strip()
            else:
                codpro = str(prd.id)
            prod['codpro'] = codpro[:15]

            lista.append(prod)
        return json.dumps(lista)      

    #@http.route('/clientecnpj', type='http', auth="public", csrf=False)
    #def website_clientecnpj(self, **kwargs):

    