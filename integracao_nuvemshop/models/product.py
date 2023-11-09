# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import requests
import unidecode


class ProductTemplate(models.Model):
    _inherit = 'product.template'
   
    @api.multi
    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        url =  '%s%s/products/'  %(self.company_id.nuvem_shop_link, self.company_id.nuvem_shop_id)
        if vals.get('online_venda') or vals.get('list_price') or vals.get('name') or vals.get('description') or vals.get('complemento') or vals.get('online_preco') or vals.get('online_estoque') or vals.get('default_code') or (vals.get('online_estoque') == 0):
            peso = self.peso or '0.0'
            altura = self.altura or '0.0'
            largura = self.largura or '0.0'
            comprimento = self.comprimento or '0.0'
            descricao = self.description or ''
            prod_name = self.name 
            prod_name = unidecode.unidecode(prod_name)
            descricao = ''
            if self.description and self.description.strip():
                descricao = unidecode.unidecode(self.description.replace('\n',''))
            headers = {
                 'Content-Type': 'application/json; charset=utf-8',
                 'User-Agent': 'Awesome app (awesome@app.com)',
                 'Authentication': '%s' %(self.company_id.nuvem_shop_authentication) 
                 }
            if self.online_venda:
                variant_ids = self.env['product.product'].sudo().search([('product_tmpl_id','=',self.id)])
                if not self.item_id:
                    values = """{"name": {"en": "%s","es": "%s","pt": "%s"},\
                            "description": {"en": "%s", "es": "%s", "pt": "%s"}, "variants":[""" %(
                            prod_name, prod_name, prod_name, 
                            descricao,descricao,descricao
                        )
                    if len(self.attribute_line_ids) == 2:
                        values = """{"name": {"en": "%s","es": "%s","pt": "%s"},\
                            "description": {"en": "%s", "es": "%s", "pt": "%s"},\
                            "attributes": [{"pt": "Tamanho"}, {"pt": "Cor"}], "variants": [""" %(
                            prod_name, prod_name, prod_name, 
                            descricao,descricao,descricao
                        )
                    if len(self.attribute_line_ids) == 1:
                        values = """{"name": {"en": "%s","es": "%s","pt": "%s"},\
                            "description": {"en": "%s", "es": "%s", "pt": "%s"},\
                            "attributes": [{"pt": "Tamanho"}], "variants": [""" %(
                            prod_name, prod_name, prod_name, 
                            descricao,descricao,descricao
                        )

                    var_prod = ''
                    estoque = self.online_estoque
                    preco = self.online_preco or self.lst_price
                    tamanho = self.complemento or 'null'
                    cor = ''
                    for variant in variant_ids:
                        estoque = variant.qty_available or variant.online_estoque or 0.0
                        if variant.online_preco:
                            preco = variant.online_preco
                        for item in variant.attribute_value_ids:
                            if 'Tamanho' in item.attribute_id.name:
                                tamanho = item.name
                            if 'Cor' in item.attribute_id.name:
                                cor = item.name
                        if var_prod != '':
                            var_prod += ', '
                        if len(self.attribute_line_ids) == 2:
                            var_prod += '{"price": "%s","stock_management": true,"stock": %s,"weight": "%s","sku": "%s"\
                                ,"width": %s, "height": %s, "depth": %s, "values": [{"pt": "%s"}, {"pt": "%s"}]}' %(
                                preco, str(int(estoque)), peso, self.default_code,
                                largura, altura, comprimento, tamanho, cor)
                        if len(self.attribute_line_ids) == 1:
                            var_prod += '{"price": "%s","stock_management": true,"stock": %s,"weight": "%s","sku": "%s"\
                                ,"width": %s, "height": %s, "depth": %s, "values": [{"pt": "%s"}]}' %(
                                preco, str(int(estoque)), peso, self.default_code,
                                largura, altura, comprimento, tamanho)
                    # so entra aqui se nao tiver variant entao nao entra
                    if var_prod == '':
                        var_prod += '{"price": "%s","stock_management": true,"stock": %s,"weight": "%s","sku": "%s"\
                            ,"width": %s, "height": %s, "depth": %s}' %(
                            self.online_preco, str(int( self.online_estoque)), peso, self.default_code,
                            largura, altura, comprimento)
                    values = values + var_prod + """]}"""
                    print((values))
                    self.message_post(body=_("Nuvem post: <em>%s</em>") % (values))
                    r = requests.post(url, headers=headers, data=values)
                    if r.status_code != 201:
                        msg_err = 'Erro ao ativar o produto na loja virtual: %s, %s' %(r.status_code, values)
                        raise UserError(msg_err)                    
                    else:
                        x = r.json()
                        fez = 'N'
                        for z in x['variants']:
                            if fez == 'N':
                                self.write({'item_id': x['id'],
                                    'variant_id': z['id']})
                                fez = 'S'
                            for variant in variant_ids:
                                for vr in variant.attribute_value_ids:
                                    if z['values'] and z['values'][0]['pt'] == vr.name:
                                        variant.write({'item_id': x['id'],
                                            'variant_id': z['id']})
                else:   # atualiza o item
                    prod = self.item_id
                    if vals.get('name') or vals.get('description') or vals.get('complemento'):
                        values = """{"id": %s,"published": true, "name": {"en": "%s","es": "%s","pt": "%s"}, "description": {"pt": "<p>%s</p>"}}""" %(
                            str(self.item_id), prod_name, prod_name, 
                            prod_name, descricao)
                        link = '%s%s' %(  
                            url,
                            str(self.item_id))
                        print((values))
                        self.message_post(body=_("Nuvem put: <em>%s</em>") % (values))
                        r = requests.put(link, headers=headers, data=values)
                        if r.status_code != 200:
                            msg_err = 'Erro ao ativar o produto na loja virtual: %s' %(r.status_code)
                            raise UserError(msg_err)
                    # Variantes
                    if self.qty_available or vals.get('online_preco') or vals.get('online_estoque') or vals.get('online_estoque') == 0  or vals.get('default_code'): 
                        estoque = 0
                        preco = self.online_preco or self.lst_price
                        variant_id = self.variant_id
                        tamanho = ''
                        cor = ''
                        for variant in variant_ids:
                            estoque = variant.qty_available or variant.online_estoque
                            if estoque < 0:
                                estoque = 0
                            if variant.online_preco:
                                preco = variant.online_preco
                            else:
                                preco = variant.lst_price
                            variant_id = variant.variant_id
                            for item in variant.attribute_value_ids:
                                if 'Tamanho' in item.attribute_id.name:
                                    tamanho = item.name
                                if 'Cor' in item.attribute_id.name:
                                    cor = item.name
                            values = """{"id": %s,"product_id": %s, "price": "%s","stock": %s,"weight": "%s","sku": "%s",\
                                "width": %s, "height": %s}""" %(
                                variant_id, str(self.item_id), 
                                preco, 
                                str(int(estoque)), peso, self.default_code,
                                largura, altura)
                            link = '%s%s/variants/%s' %(  
                                url,
                                str(self.item_id), str(self.variant_id))
                            print((values))
                            self.message_post(body=_("Nuvem put: <em>%s</em>") % (values))
                            r = requests.put(link, headers=headers, data=values)
                            if r.status_code != 200:
                                msg_err = 'Erro ao ativar o produto na loja virtual: %s' %(r.status_code)
                                raise UserError(msg_err)
            else:  # desmarcou vendas online
                if self.item_id and not self.online_venda:
                    prod = """{"id": %s, "published": "%s"}""" %(
                    self.item_id, 'false')
                    link = '%s%s' %(  
                        url,
                        str(self.item_id))
                    print((values))
                    self.message_post(body=_("Nuvem put: <em>%s</em>") % (values))
                    r = requests.put(link, headers=headers, data=prod)
                    if r.status_code != 200:
                        msg_err = 'Erro ao inativar o produto na loja virtual: %s' %(r.status_code)
                        raise UserError(msg_err)
        return res

class ProductProduct(models.Model):
    _inherit = 'product.product'
   
    @api.multi
    def write(self, vals):
        res = super(ProductProduct, self).write(vals)
        if len(self) > 1:
            return res
        url =  '%s%s/products/'  %(
                        self.product_tmpl_id.company_id.nuvem_shop_link, 
                        self.product_tmpl_id.company_id.nuvem_shop_id)
        if vals.get('online_venda') or vals.get('name') or vals.get('description') or vals.get('complemento') or vals.get('online_preco') or vals.get('online_estoque') or vals.get('online_estoque') == 0:
            peso = self.peso or '0.0'
            altura = self.altura or '0.0'
            largura = self.largura or '0.0'
            comprimento = self.comprimento or '0.0'
            tamanho = self.complemento or 'null'
            descricao = self.description or ''
            prod_name = self.name 
            prod_name = unidecode.unidecode(prod_name)
            descricao = ''
            if self.description and self.description.strip():
                descricao = unidecode.unidecode(self.description.replace('\n',''))
            headers = {
                 'Content-Type': 'application/json; charset=utf-8',
                 'User-Agent': 'Awesome app (awesome@app.com)',
                 'Authentication': '%s' %(self.product_tmpl_id.company_id.nuvem_shop_authentication) 
                 }
            if self.online_venda:
                url =  '%s%s/products/'  %(
                        self.product_tmpl_id.company_id.nuvem_shop_link, 
                        self.product_tmpl_id.company_id.nuvem_shop_id)
                if not self.item_id:
                    if len(self.attribute_line_ids) == 2:
                        values = """{"name": {"en": "%s","es": "%s","pt": "%s"},\
                            "description": {"en": "%s", "es": "%s", "pt": "%s"},\
                            "attributes": [{"pt": "Tamanho"}, {"pt": "Cor"}], "variants": [""" %(
                            prod_name, prod_name, prod_name, 
                            descricao,descricao,descricao
                        )
                    if len(self.attribute_line_ids) == 1:
                        values = """{"name": {"en": "%s","es": "%s","pt": "%s"},\
                            "description": {"en": "%s", "es": "%s", "pt": "%s"},\
                            "attributes": [{"pt": "Tamanho"}], "variants": [""" %(
                            prod_name, prod_name, prod_name, 
                            descricao,descricao,descricao
                        )
                    variant_ids = self.env['product.product'].sudo().search([('product_tmpl_id','=',self.id)])
                    var_prod = ''
                    preco = self.online_preco or self.lst_price
                    for variant in variant_ids:
                        estoque = variant.qty_available
                        if variant.online_preco:
                            preco = variant.online_preco
                        tamanho = ''
                        cor = ''
                        for item in variant.attribute_value_ids:
                            if 'Tamanho' in item.attribute_id.name:
                                tamanho = item.name
                            if 'Cor' in item.attribute_id.name:
                                cor = item.name
                        if var_prod != '':
                            var_prod += ', '
                        if len(self.attribute_line_ids) == 1:
                            var_prod += '{"price": "%s","stock_management": true,"stock": %s,"weight": "%s","sku": "%s"\
                                ,"width": %s, "height": %s, "depth": %s, "values": [{"pt": "%s"}]}' %(
                                preco, str(int(estoque)), peso, self.default_code,
                                largura, altura, comprimento, tamanho)
                        else:
                            var_prod += '{"price": "%s","stock_management": true,"stock": %s,"weight": "%s","sku": "%s"\
                                ,"width": %s, "height": %s, "depth": %s, "values": [{"pt": "%s"},{"pt": "%s"}]}' %(
                                preco, str(int(estoque)), peso, self.default_code,
                                largura, altura, comprimento, tamanho, cor)
                    if var_prod == '':
                        var_prod += '{"price": "%s","stock_management": true,"stock": %s,"weight": "%s","sku": "%s"\
                            ,"width": %s, "height": %s, "depth": %s}' %(
                            self.online_preco, str(int( self.qty_available)), peso, self.default_code,
                            largura, altura, comprimento)
                    values = values + var_prod + """]}"""
                    print((values))
                    self.message_post(body=_("Nuvem post: <em>%s</em>") % (values))
                    r = requests.post(url, headers=headers, data=values)
                    if r.status_code != 201:
                        msg_err = 'Erro ao inserir produto na loja virtual: %s' %(r.status_code)
                        raise UserError(msg_err)                    
                    else:
                        x = r.json()
                        fez = 'N'
                        for z in x['variants']:
                            if fez == 'N':
                                self.write({'item_id': x['id'],
                                    'variant_id': z['id']})
                                fez = 'S'
                            for variant in variant_ids:
                                if z['values'][0]['pt'] == variant.attribute_value_ids.name:
                                    variant.write({'item_id': x['id'],
                                        'variant_id': z['id']})
                else:
                    prod = self.item_id
                    # Variantes
                    if vals.get('online_preco') or vals.get('online_estoque') or vals.get('online_estoque') == 0  or vals.get('default_code'): 
                        estoque = self.qty_available
                        preco = self.online_preco or self.lst_price
                        values = """{"price": "%s","stock": %s}""" %(
                            preco, str(int(estoque)))
                        link = '%s%s/variants/%s' %(  
                            url,
                            str(self.item_id), str(self.variant_id))
            else:
                if self.item_id and not self.online_venda:
                    prod = """{"id": %s, "published": "%s"}""" %(
                    self.item_id, 'false')
                    link = '%s%s' %(  
                        url,
                        str(self.item_id))
                    print((values))
                    self.message_post(body=_("Nuvem put: <em>%s</em>") % (values))
                    r = requests.put(link, headers=headers, data=prod)
                    if r.status_code != 200:
                        msg_err = 'Erro ao inativar produto na loja virtual: %s' %(r.status_code)
                        raise UserError(msg_err)
        return res
