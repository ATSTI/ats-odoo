# -*- coding: utf-8 -*-
# © 2016 Alessandro Fernandes Martini <alessandrofmartini@gmail.com>, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import base64

from lxml import objectify
from dateutil import parser
from random import SystemRandom
from datetime import  datetime

from odoo import api, models, fields
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class WizardImportNfe(models.TransientModel):
    _name = 'wizard.import.nfe'

    nfe_xml = fields.Binary(u'XML da NFe')
    purchase_id = fields.Many2one('purchase.order',
                                  string='Pedido')
    fiscal_position_id = fields.Many2one('account.fiscal.position',
                                         string='Posição Fiscal')
    payment_term_id = fields.Many2one('account.payment.term',
                                      string='Forma de Pagamento')
    not_found_product = fields.Many2many('not.found.products', string="Produtos não encontrados")
    found_product = fields.Many2many('found.products', string="Produtos encontrados")
    confirma = fields.Boolean(string='Confirmar')
    altera = fields.Boolean(string='Alterar')
    order_line = fields.Many2many('purchase.order.line',string="Ordem dos produtos")
    nfe_num = fields.Integer('Num. NFe')
    nfe_serie = fields.Char('Série')
    nfe_modelo = fields.Char('Modelo')
    nfe_chave =  fields.Char('Chave NFe')
    nfe_emissao = fields.Date('Data Emissão NFe')

#---------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------minha rotina-----------------------------------------------------------#
#---------------------------------------------------------------------------------------------------------------------#

    def retorna_data(self, nfe):
        ide = nfe.NFe.infNFe.ide
        day = str(ide.dhEmi).split('T')
        hour = day[1].split('-')
        datehour = day[0] + ' ' + hour[0]
        datetime_obj = datetime.strptime(datehour, '%Y-%m-%d %H:%M:%S')
        return datetime_obj

    def arruma_cpf_cnpj(self, partner_doc):
        if len(partner_doc) > 11:
            if len(partner_doc) < 14:
                partner_doc = partner_doc.zfill(14)
            partner_doc = "%s.%s.%s/%s-%s" % ( partner_doc[0:2], partner_doc[2:5], partner_doc[5:8], partner_doc[8:12], partner_doc[12:14] )
        else:
            if len(partner_doc) < 11:
                partner_doc = partner_doc.zfill(11)
            partner_doc = "%s.%s.%s-%s" % (partner_doc[0:3], partner_doc[3:6], partner_doc[6:9], partner_doc[9:11])
        return partner_doc

    def get_main_purchase(self, nfe):
        ide = nfe.NFe.infNFe.ide
        num_nfe = nfe.NFe.infNFe.ide.nNF
        chave = nfe.protNFe.infProt.chNFe
        #dest = nfe.NFe.infNFe.dest
        emit = nfe.NFe.infNFe.emit
        partner_doc = emit.CNPJ if hasattr(emit, 'CNPJ') else emit.CPF
        partner_doc = str(partner_doc)
        partner_doc = self.arruma_cpf_cnpj(partner_doc)
        partner = self.env['res.partner'].search([
            ('cnpj_cpf', '=', partner_doc)])
        if not partner:
            raise UserError('Fornecedor não encontrado, por favor, crie um fornecedor com CPF/CNPJ igual a ' + partner_doc)
        order = self.env['purchase.order'].search([
            ('partner_id', '=', partner.id),
            ('partner_ref', '=', num_nfe)
        ])
        if order:
            raise UserError('Nota já importada')

        datetime_obj = self.retorna_data(nfe)
        return dict(
            partner_id=partner.id,
            date_planned=datetime_obj,
            date_order=datetime_obj,
            payment_term_id=self.payment_term_id.id,
            fiscal_position_id=self.fiscal_position_id.id,
            partner_ref=num_nfe,
            nfe_num=num_nfe,
            nfe_emissao=datetime_obj,
            nfe_serie = nfe.NFe.infNFe.ide.serie,
            nfe_modelo= nfe.NFe.infNFe.ide.mod,
            nfe_chave = chave,
        )

    def create_order_line(self, item, nfe, order_id, nitem):
        emit = nfe.NFe.infNFe.emit
        partner_doc = emit.CNPJ if hasattr(emit, 'CNPJ') else emit.CPF
        partner_id = self.env['res.partner'].search([('cnpj_cpf', '=', self.arruma_cpf_cnpj(str(partner_doc)))]).id
        uom_id = self.env['uom.uom'].search([
            ('name', '=', str(item.prod.uCom))], limit=1).id
        # 21/09/2022 busca ta errado o codigo do fornecedor nao eo mesmo
        #product = self.env['product.product'].search([
        #    ('default_code', '=', item.prod.cProd)], limit=1)
        product = ''
        if not product:
            if item.prod.cEAN != 'SEM GTIN':
                product = self.env['product.product'].search([
                    ('barcode', '=', item.prod.cEAN)], limit=1)
        if not product:
            product_code = self.env['product.supplierinfo'].search([
                ('product_code', '=', item.prod.cProd), ('name', '=', partner_id)
            ])
            #product = self.env['product.product'].browse(product_code.product_tmpl_id.id)
            product = self.env['product.product'].search([('product_tmpl_id', '=', product_code.product_tmpl_id.id)])
            #product = product_code.product_id
        if not product:
            if item.prod.xProd:
                product = self.env['product.template'].search([
                    ('name', 'ilike', item.prod.xProd)], limit=1)
            if product:
                product = self.env['product.product'].search([('product_tmpl_id', '=', product.id)])

        if not product:
            if self.not_found_product:
                for line in self.not_found_product:
                    if line.name == item.prod.xProd:
                        if line.product_id:
                            product = self.env['product.product'].browse(line.product_id.id)
                            # cadastra o produto no
                            prd_ids = {}
                            prd_ids['product_id'] = line.product_id.id
                            prd_ids['product_tmpl_id'] = line.product_id.product_tmpl_id.id
                            prd_ids['name'] = partner_id
                            prd_ids['product_name'] = str(item.prod.xProd)
                            prd_ids['product_code'] = str(item.prod.cProd)
                            self.env['product.supplierinfo'].create(prd_ids)
                            break
                        else:
                            vals = {}
                            vals['name'] = str(item.prod.xProd)
                            vals['default_code'] = str(item.prod.cProd)
                            if uom_id:
                                vals['uom_id'] = uom_id
                            else:
                                vals['uom_id'] = 1
                            vals['type'] = 'product'
                            vals['list_price'] = float(item.prod.vUnCom)
                            vals['purchase_method'] = 'receive'
                            vals['tracking'] = 'none'
                            try:
                                if item.prod.cEAN != 'SEM GTIN':
                                    vals['barcode'] = item.prod.cEAN
                            except:
                                x = 1
                            vals['type'] = 'product'
                            vals['fiscal_type'] = 'product'
                            vals['l10n_br_sped_type'] = '00'
                            ncm = str(item.prod.NCM).zfill(8)
                            #ncm = '%s.%s.%s' % (ncm[:4], ncm[4:6], ncm[6:8])
                            pf_ids = self.env['product.fiscal.classification'].search([('code', '=', ncm)])
                            if not pf_ids:
                                pf_ids = self.env['product.fiscal.classification'].search([('code', '=', str(item.prod.NCM))])
                            vals['fiscal_classification_id'] = pf_ids.id
                            product = self.env['product.product'].create(vals)
                            break
        product_id = product.id
        quantidade = item.prod.qCom
        preco_unitario = item.prod.vUnCom
        uom_xml = self.env['uom.uom'].search([('name','=',str(item.prod.uCom))],limit=1)
        datetime_obj = self.retorna_data(nfe)
        return self.env['purchase.order.line'].create({
            'product_id': product_id,'name':item.prod.xProd,'date_planned':datetime_obj,
            'product_qty': quantidade, 'price_unit': preco_unitario, 'product_uom':product.uom_id.id,
            'order_id':order_id,'partner_id':partner_id, 'product_qty_xml':float(quantidade), 'product_uom_xml':uom_xml.id,
            'num_item_xml':nitem
        })

    def get_items_purchase(self, nfe, order_id):
        items = []
        cont = 0
        for det in nfe.NFe.infNFe.det:
            cont = cont + 1;
            item = self.create_order_line(det, nfe, order_id, cont)
            items.append((4, item.id, False))
        return {'order_line': items}



    @api.multi
    def action_import_nfe_purchase(self):
        if not self.nfe_xml:
            raise UserError('Por favor, insira um arquivo de NFe.')
        nfe_string = base64.b64decode(self.nfe_xml)
        nfe = objectify.fromstring(nfe_string)
        purchase_dict = {}
        purchase_dict.update(self.get_main_purchase(nfe))
        order = self.env['purchase.order'].create(purchase_dict)
        purchase_dict = {}
        order_id = order.id
        purchase_dict.update(self.get_items_purchase(nfe, order_id))
        order.write(purchase_dict)
        order._compute_tax_id()

    def carrega_produtos(self, item, nfe):
        product = ''
        # 21/09/2022 busca ta errado o codigo do fornecedor nao eo mesmo
        #product = self.env['product.product'].search([
        #    ('default_code', '=', item.prod.cProd)], limit=1)
        #if not product:
        if item.prod.cEAN != 'SEM GTIN':
            product = self.env['product.product'].search([
                    ('barcode', '=', item.prod.cEAN)], limit=1)
        if not product:
            emit = nfe.NFe.infNFe.emit
            partner_doc = emit.CNPJ if hasattr(emit, 'CNPJ') else emit.CPF
            partner_id = self.env['res.partner'].search([('cnpj_cpf', '=', self.arruma_cpf_cnpj(str(partner_doc)))]).id
            product_code = self.env['product.supplierinfo'].search([
                ('product_code','=',item.prod.cProd),
                ('name','=',partner_id)
            ], limit=1)
            product = self.env['product.product'].search([('product_tmpl_id', '=', product_code.product_tmpl_id.id)])
        if not product:
            if item.prod.xProd:
                product = self.env['product.template'].search([
                    ('name', 'ilike', item.prod.xProd)], limit=1)
        if not product:
            return self.env['not.found.products'].create({
                'name':item.prod.xProd
            })
        else:
            return False


    def checa_produtos(self):
        if not self.nfe_xml:
            raise UserError('Por favor, insira um arquivo de NFe.')
        nfe_string = base64.b64decode(self.nfe_xml)
        nfe = objectify.fromstring(nfe_string)
        items = []
        for det in nfe.NFe.infNFe.det:
            item = self.carrega_produtos(det, nfe)
            if item:
                items.append(item.id)
        if items:
            self.not_found_product = self.env['not.found.products'].browse(items)
        self.confirma = True
        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wizard.import.nfe',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }




    def action_altera_compra(self):
        linhas = []
        nfe_prod = []
        for line in self.purchase_id.order_line:
            linhas.append(line.id)
        if linhas:
            self.order_line = self.env['purchase.order.line'].browse(linhas)
        if not self.nfe_xml:
            raise UserError('Por favor, insira um arquivo de NFe.')
        nfe_string = base64.b64decode(self.nfe_xml)
        nfe = objectify.fromstring(nfe_string)
        date_nfe = self.retorna_data(nfe)
        self.nfe_num = nfe.NFe.infNFe.ide.nNF
        self.nfe_serie = nfe.NFe.infNFe.ide.serie
        self.nfe_modelo = nfe.NFe.infNFe.ide.mod
        self.nfe_chave = nfe.protNFe.infProt.chNFe
        self.nfe_emissao = date_nfe.strftime(DEFAULT_SERVER_DATE_FORMAT)
        for det in nfe.NFe.infNFe.det:
            vals = {}
            vals['name'] = det.prod.xProd
            #vals['purchase'] = self.purchase_id
            vals['num_item_xml'] = int(det.get('nItem'))
            vals['product_uom_xml'] = det.prod.uCom
            vals['product_qty_xml'] = det.prod.qCom
            vals['purchase_id'] = self.purchase_id.id
            
            nfe_prod.append(self.env['found.products'].create(vals).id)
        self.found_product = self.env['found.products'].browse(nfe_prod)
        self.altera = True
        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wizard.import.nfe',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }


    def action_edit_nfe_purchase(self):
        #cont_nfe = 0
        #cont_odoo = 0
        #if not self.nfe_xml:
        #    raise UserError('Por favor, insira um arquivo de NFe.')
        #nfe_string = base64.b64decode(self.nfe_xml)
        #nfe = objectify.fromstring(nfe_string)
        #num_itens = len(self.found_product)
        #for l in self.found_product:
        #    if l.
        """
        for l in self.found_product:
            cont_odoo = 0
            cont_nfe = cont_nfe + 1
            for order in self.order_line:
                cont_odoo = cont_odoo + 1
                if cont_odoo == l.sequence:
                    cont = 0
                    for det in nfe.NFe.infNFe.det:
                        cont = cont + 1
                        if det.prod.xProd == l.name:
                            order.num_item_xml = cont
                            uom_xml = self.env['product.uom'].search([('name', '=', str(det.prod.uCom))], limit=1)
                            order.product_uom_xml = uom_xml
                            order.product_qty_xml = det.prod.qCom
                            break
                    break
        """
        vals = {}
        vals['nfe_num'] = self.nfe_num
        vals['nfe_serie'] = self.nfe_serie
        vals['nfe_modelo'] = self.nfe_modelo
        vals['nfe_chave'] = self.nfe_chave
        vals['nfe_emissao'] = self.nfe_emissao

        self.purchase_id.write(vals)
        
        for l in self.found_product:
            #for order in self.order_line:
            #cont_odoo = cont_odoo + 1
            uom_xml = self.env['uom.uom'].search([('name','=',str(l.product_uom_xml))],limit=1)
            if not uom_xml:
                raise UserError('Unidade de Medida não cadastrada: ' + str(l.product_uom_xml))
            ord_ids = self.env['purchase.order.line'].search([
                ('order_id', '=', self.purchase_id.id), 
                ('product_id','=',l.product_id.product_id.id)], limit=1)
                
            if ord_ids:     
                vals = {}
                vals['name'] =  l.name
                vals['num_item_xml'] =  l.num_item_xml
                vals['product_uom_xml'] = uom_xml.id
                vals['product_qty_xml'] = l.product_qty_xml
                ord_ids.write(vals)
            """  
            if cont_odoo == l.sequence:
                cont = 0
            for det in nfe.NFe.infNFe.det:
                cont = cont + 1
                if det.prod.xProd == l.name:
                            order.num_item_xml = cont
                            uom_xml = self.env['product.uom'].search([('name', '=', str(det.prod.uCom))], limit=1)
                            order.product_uom_xml = uom_xml
                            order.product_qty_xml = det.prod.qCom
                            break
                    break
             """


class NotFoundProduct(models.Model):
    _name = 'not.found.products'

    product_id = fields.Many2one('product.product',string="Produto do Odoo")
    name = fields.Char(string="Produto da NFe")
    sequence = fields.Integer(string="Sequencia", default=10)

class FoundProduct(models.Model):
    _name = 'found.products'

    name = fields.Char(string="Produto da NFe")
    sequence = fields.Integer(string="Sequencia", default=10)
    product_id = fields.Many2one('purchase.order.line', 
        string="Produto do Odoo" ,
        domain="[('order_id', '=', purchase_id)]"
        )
    purchase_id = fields.Many2one('purchase.order',
                                  string='Pedido')    
    num_item_xml = fields.Integer('N.Item')
    product_uom_xml = fields.Char(string='Un.(xml)')
    product_qty_xml = fields.Float(string='Qtde(xml)')
    #line_id = fields.Integer('Linha Pedido')
