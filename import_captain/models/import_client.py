# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.addons.br_base.tools import fiscal
import csv
from datetime import datetime, date
import tempfile
import xlrd
import re
import time

_TASK_STATE = [('open', 'Novo'),('done', 'Importado'), ('cancelled', 'Cancelado')]

"""
def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, charset='utf-8', **kwargs):
    # csv.py doesn't do Unicode; encode temporarily as UTF-8:
    #csv_reader = csv.reader(utf_8_encoder(unicode_csv_data, charset),
    #                        dialect=dialect, **kwargs)
    #for row in csv_reader:
        # decode UTF-8 back to Unicode, cell by cell:
    #    yield [unicode(cell, charset) for cell in row]
    print 'aqui'


def utf_8_encoder(unicode_csv_data, charset):
    #for line in unicode_csv_data:
    #    yield line
        #yield line.decode(charset).encode('utf-8', 'ignore')
    print 'aqui'
"""

class import_client(models.Model):
#class ea_import_chain(osv.osv):

    _name = 'import.client'
    
    name = fields.Char('Descrição', size=256, required=True)
    num_ini = fields.Integer('Numero Inicial')
    num_fim = fields.Integer('Numero Final')
    input_file = fields.Binary('Arquivo', required=False)
    user_id = fields.Many2one('res.users', 'Inserido por', track_visibility='onchange'
        )
    header =  fields.Boolean('Header')
    state = fields.Selection(_TASK_STATE, 'Situacao', required=True, default='open')

    def set_done(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'done'}, context=context)

    def set_open(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'open'}, context=context)

    def set_cancelled(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'cancelled'}, context=context)

    def incluir_cliente(self, codigo):
        vals = {}
        vals['name'] = '%s-Contas a Pagar' %(codigo)
        vals['legal_name'] = '%s-Contas a Pagar' %(codigo)
        vals['street'] = 'Rua Contas a pagar'
        vals['country_id'] = 32
        vals['state_id'] = 95
        vals['city_id'] = 3144
        vals['district'] = 'Contas a pagar'
        vals['zip'] = '05014000'
        vals['cod_service'] = codigo
        vals['ref'] = codigo
        rp_id = self.env['res.partner'].create(vals)
        return rp_id
        

    def cep(self, cep):
        cep = str(cep)
        contact_values = {}
        if len(cep) < 9:
            cep = cep.zfill(8)
            cep = "%s-%s" %(cep[0:5],cep[5:8])
        try:
            res = self.env['br.zip'].search_by_zip(zip_code=cep)
        except:
            print ('errocep')
        if res:
            contact_values['zip'] = res['zip']
            if res['district']:
                contact_values['district'] = res['district']
            else:
                contact_values['district'] = bairro
            contact_values['city_id'] = res['city_id']
            contact_values['country_id'] = res['country_id']
            contact_values['state_id'] = res['state_id']
            if res['street']:
                contact_values['street'] = res['street']
            else:
                contact_values['street'] = endereco
        return contact_values
        

    def endereco(self, endereco, 
        bairro, cidade, number, pais, estado, cep,
        complemento, name, tipo, email, fone):
        contact_values = {}
        contact_values = self.cep(cep)
        if not contact_values:
            if len(cep) < 9:
                cep = cep.zfill(8)
                cep = "%s-%s" %(cep[0:5],cep[5:8])
            # Nao achou CEP
            contract_values['zip'] = cep
            if endereco:
                contact_values['street'] = endereco
            if pais:
                contact_values['country_id'] = self.env['res.country'].search([('name','ilike',str(pais).lower())],limit=1).id
                if 'country_id' not in contact_values:
                    vals['country_id'] = self.env['res.country'].search([('name','=','Brasil')],limit=1).id 

            if estado:
                contact_values['state_id'] = self.env['res.country.state'].search([('code','=',str(estado))]).id
            city_id = self.env['res.state.city'].search([('name','ilike',cidade)],limit=1).id
            if not city_id:
                if cidade == 'SAO PAULO':
                    cidade = u'SÃO PAULO' 
                    contact_values['city_id'] = self.env['res.state.city'].search([('name','ilike',cidade)],limit=1).id
            else:
                contact_values['city_id'] = city_id
            if bairro:
                contact_values['district'] = bairro
        contact_values['number'] = number
        if email:
            contact_values['email'] = email
        if tipo:
            contact_values['type'] = tipo
        if name:
            contact_values['name'] = name
        if fone:
            contact_values['fone'] = fone
            
        return contact_values
    
    
    def import_to_xls(self):
        client_id = 0
        client_obj = self.env['res.partner']
        if not self.env['res.partner']:
            file_path = '/opt/odoo/captain.xls'
            #file_path = '/home/odoo/cliente_2018.xls'
            book = xlrd.open_workbook(file_path)
            first_sheet = book.sheet_by_index(0)
            cnpj_jafoi = ''
            parent_id = 0
            vendedor_id = 0
            conta_registros = 0
            tempo = 3
            linha = 1
            vals = {}
            for rownum in range(first_sheet.nrows):                                                                                                       
                rowValues = first_sheet.row_values(rownum)
                ativo = True
                cli = True
                        

                valor = 0.0
                if rownum > self.num_ini and rownum < self.num_fim and cli:
                    anotacoes = ''
                    cobranca = {}
                    cnpj_cpf = '' #rowValues[3]  
                    if linha == 1: 
                        nome = u'%s' %(rowValues[1])
                        nome_cliente = nome
                        codigo = int(rowValues[0])
                        if rowValues[14]:
                            if str(rowValues[14]) != '55.0':
                                vals['phone'] = rowValues[14]
                        if rowValues[15]:
                            if str(rowValues[15]) != '55.0':
                                vals['mobile'] = str(rowValues[15])
                        vals['ref'] = codigo
                        
                        vals['name'] = nome_cliente
                        nome_cli = '%s-Contas a Pagar' %(str(codigo))
                        if rowValues[8]:
                            vals['street'] = rowValues[8]
                        #if rowValues[2]:
                        #    vals['street2'] = rowValues[2]
                        zip = ''
                        if rowValues[6]:
                            zip = rowValues[6]
                        if zip:
                            try:
                                cep = str(int(rowValues[6]))
                            except:
                                cep = str(rowValues[6])    
                            try:
                                if len(cep) == 8:
                                    zip = "%s-%s" %(cep[0:5],cep[5:8])
                                elif len(cep) == 9:
                                    zip = rowValues[6]
                                time.sleep( tempo )
                                res = self.env['br.zip'].search_by_zip(zip_code=zip)
                                if res:
                                    vals['zip'] = res['zip']
                                    vals['district'] = res['district']
                                    vals['city_id'] = res['city_id']
                                    vals['country_id'] = res['country_id']
                                    vals['street'] = res['street']
                                    vals['state_id'] = res['state_id']
                                if tempo == 9:
                                   tempo = 3
                                else:
                                   tempo += 1
                            except:
                                pass
                        """    
                        else:
                            if rowValues[13]:
                                if rowValues[13] == 'BRAZIL':
                                    pais = 'Brasil'
                                else:
                                    pais = rowValues[13]
                                vals['country_id'] = self.env['res.country'].search([('name','ilike',str(pais.lower()))],limit=1).id
                            if rowValues[5]:
                                uf = self.env['res.country.state'].search([('code','=',str(rowValues[5]))], limit=1)
                                if uf:
                                    vals['state_id'] = uf.id
                            if rowValues[7]:
                                vals['city_id'] = self.env['res.state.city'].search([('name','ilike',str(rowValues[7]))],limit=1).id
                        if 'country_id' not in vals:
                            vals['country_id'] = self.env['res.country'].search([('name','=','Brasil')],limit=1).id
                        """    
                        if rowValues[3]:
                            vals['cnpj_cpf'] = rowValues[3]
                        vals['rg_fisica'] = rowValues[4]
                         
                        partner = self.env['res.partner'].search([('name','ilike',nome_cliente)],limit=1)
                        if partner:
                            """
                            altera = {}
                            if 'cnpj_cpf' in vals:
                                altera['cnpj_cpf']= vals['cnpj_cpf']
                            if 'rg_fisica' in vals:
                                altera['rg_fisica']= vals['rg_fisica']
                            partner.write(altera) 
                            linha = 1
                            vals = {}
                            """
                            continue
                   
                    empresa = False
                    print ('Importando Cliente ... - %s ...' %(str(rowValues[0])))
                    vals['company_type'] = 'person'

                    
                    # complemento endereco
                        
                    #@@@ ?
                    if rowValues[16]:
                        vals['email'] = rowValues[16]
                    # Endereco Principal    
                    #endereco = rowValues[8]  
                    number = ''
                    if rowValues[2]:
                        try:
                            number = str(int(rowValues[2]))
                        except:
                            number = rowValues[2]
                    vals['number'] = number
                    #bairro = rowValues[10]                   
                         
                    p_id =  client_obj.sudo().create(vals)
                    #else:
                    #    partner.sudo().write(vals)
                    #    p_id = partner
                    linha = 1  
                    self.env.cr.commit()
                    vals = {}
                    conta_registros += 1
                  
                    
        return client_id

