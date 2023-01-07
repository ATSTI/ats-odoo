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
        

    def endereco(self, linha):
        contact_values = {}
        #contact_values = self.cep(cep)
        #import pudb;pu.db
        p1 = linha.find('-')
        p2 = linha[p1+1:len(linha)].find('-')
        p3 = linha[p1+p2+2:len(linha)].find('-')
        p4 = linha[p1+p2+p3+3:len(linha)].find('-')
        p5 = linha[p1+p2+p3+p4+4:len(linha)].find('-')
        p6 = linha[p1+p2+p3+p4+p5+5:len(linha)].find('-')
        bairro = ''
        numero = ''
        #import pudb;pu.db
        if (p6 == 6):
            num = linha[:p1].find(',')
            rua = linha[:num]
            numero = linha[num+1:p1]
            bairro = linha[p1+1:p2+p1+1]
            cidade = linha[p1+p2+p3+3:p4+p3+p2+p1+3]
            uf = linha[len(linha)-14:len(linha)-12]
            cep = linha[len(linha)-9:len(linha)]
        elif (p6 == -1):
            num = linha[:p1].find(',')
            if num > -1:
                rua = linha[:num]
                numero = linha[num+1:p1]
            else:
                rua = linha[:p1]
                bairro = linha[p1+1:p2+p1+1]
            cidade = linha[p1+p2+2:p3+p2+p1+1]
            uf = linha[len(linha)-14:len(linha)-12]
            cep = linha[len(linha)-9:len(linha)]
        else:
            import pudb;pu.db
            x = 1
            # se nao tem bairro, entao vai ate o p5 apenas
            # parou aqui , entao deu erro na contagem de '-'

        contact_values['zip'] = cep.strip()
        contact_values['street'] = rua.strip()
        if bairro:
            contact_values['district'] = bairro.strip()
        
        uf = uf.strip()
        state_id = self.env['res.country.state'].search([
            ('code','=',uf),('country_id','=',31)])
        #for st in state_id:
        #    x = st.country_id.name
        #    , ('country_id','=','')
        cidade = cidade.strip()
        city_id = self.env['res.state.city'].search([
            ('name','ilike',cidade), ('state_id','=',state_id.id)], limit=1)
        #for cty in city_id:
        if city_id:
            contact_values['city_id'] = city_id.id
            contact_values['state_id'] = city_id.state_id.id
            contact_values['country_id'] = city_id.state_id.country_id.id
        else:
            cep = cep.strip()
            #res = self.env['br.zip'].search_by_zip(zip_code=cep)
            res = ''
            try:
                res = self.env['br.zip'].search_by_zip(zip_code=cep)
            except:
                print ('errocep')
            if res:
                contact_values['zip'] = res['zip']
                contact_values['district'] = res['district']
                contact_values['city_id'] = res['city_id']
                contact_values['country_id'] = res['country_id']
                contact_values['street'] = res['street']
                contact_values['state_id'] = res['state_id']
        contact_values['number'] = numero.strip()
        
        
        #if email:
        #    contact_values['email'] = email
        #if tipo:
        #    contact_values['type'] = tipo
        #if name:
        #    contact_values['name'] = name
        #if fone:
        #    contact_values['fone'] = fone
            
        return contact_values
    
    #Importa Lista Preço 
    def import_to_xls(self):
        pr_id = 0
        pr_obj = self.env['product.pricelist']
        prod_obj = self.env['product.template']
        #file_path = '/opt/odoo/outros/diversos/lista.xls'
        file_path = '/home/odoo/importacao_br.xls'
        book = xlrd.open_workbook(file_path)
        first_sheet = book.sheet_by_index(0)
        conta_registros = 0
        tempo = 3
        linha = 1

        # LISTA ID coloque aqui o Codigo Id do odoo da lista
        lista = 1
         
        lista_ids = pr_obj.browse(lista)
        cli = self.env['res.partner'].search([('state_id','not in', (86, 91, 95, 77, 77, 83, 81, 87, 89))])
        if cli:
            cli.write({'property_product_pricelist': lista_ids.id})
        comeca_contar = 0
        for rownum in range(first_sheet.nrows): 
            rowValues = first_sheet.row_values(rownum)
            valor = 0.0
            if rownum > self.num_ini and rownum < self.num_fim and rowValues[0]:
                produto = int(rowValues[0])
                prod = prod_obj.search([('default_code','=',str(produto))])
                if prod:
                    existe = 'N'
                    for item in lista_ids.item_ids:
                        if item.product_tmpl_id.id == prod.id:
                            existe = 'S'
                    if existe == 'S':
                        continue                    
                
                    pitem = []
                    vals = {}
                
                
                    #import pudb;pu.db
                    preco = rowValues[4]
                    vals['product_tmpl_id'] = prod.id
                    vals['fixed_price'] = preco
                    vals['applied_on'] = '1_product'
                    pitem.append((0,0,vals))
                    lista_ids.write({'item_ids': pitem})
                else:
                    continue				
                			
                



""" Importa Cliente 
    def import_to_xls(self):
        client_id = 0
        client_obj = self.env['res.partner']
        if not self.env['res.partner']:
            file_path = '/opt/odoo/outros/diversos/clientes.xls'
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
            comeca_contar = 0
            cnpj_cpf = ''
            for rownum in range(first_sheet.nrows):                                                                                                       
                rowValues = first_sheet.row_values(rownum)
                ativo = True
                cli = True
                valor = 0.0
                if rownum > self.num_ini and rownum < self.num_fim and cli:
                    #import pudb;pu.db
                    def grava(values, ie, cnpj_cpf):
                        print ('Importando Cliente ... - %s ...' %(nome))
                        comeca_contar = 0
                        #import pudb;pu.db
                        try:
                            p_id =  client_obj.sudo().create(values)
                        except:
                            import pudb;pu.db
                            print ('erro aqui %' %(nome))
                        if endereco_values:
                            p_id.write(endereco_values)
                        anotacoes = ''
                        if ie and len(cnpj_cpf) > 14:
                            uf = p_id.state_id and p_id.state_id.code.lower() or ''
                            res = p_id._validate_ie_param(uf, ie)
                            if res:
                                p_id.write({'inscr_est': ie})
                            else:
                                anotacoes = 'Insc. Estadual: %s' %(ie)
                        else:
                            if ie:
                                p_id.write({'rg_fisica': ie})
                        if cnpj_cpf:
                            if len(cnpj_cpf) > 14:
                                if fiscal.validate_cnpj(cnpj_cpf):
                                    p_id.write({'cnpj_cpf': cnpj_cpf})
                                else:
                                    anotacoes += ' CNPJ: %s' %(cnpj_cpf)
                            else:
                                if fiscal.validate_cpf(cnpj_cpf):
                                    p_id.write({'cnpj_cpf': cnpj_cpf})
                                else:
                                    anotacoes += ' CPF: %s' %(cnpj_cpf)
                        if anotacoes:
                            p_id.write({'comment': anotacoes})
                        linha = 1
                        self.env.cr.commit()

                    if rowValues[1]:
                        if isinstance(rowValues[1], float):
                            if comeca_contar == 4:
                                grava(vals, ie, cnpj_cpf)
                                vals = {}
                            comeca_contar = 1
                    anotacoes = ''
                    cobranca = {}

                    if comeca_contar == 1 and rowValues[1]:
                        if not isinstance(rowValues[1], float):
                            comeca_contar = 0
                            continue
                        cnpj_cpf = ''
                        nome = u'%s' %(rowValues[2].strip())
                        nome_cliente = nome
                        codigo = int(rowValues[1])
                        vals['ref'] = codigo
                        
                        vals['name'] = nome_cliente
                        if isinstance(rowValues[4], float):
                            c = str(int(rowValues[4]))
                            cnpj_cpf = '%s.%s.%s/%s-%s' %(
                                c[:2],
                                c[2:5],
                                c[5:8],
                                c[8:12],
                                c[12:14]
                                )
                        else:
                            cnpj_cpf = rowValues[4].strip()
                        if len(cnpj_cpf) > 14:
                            vals['company_type'] = 'company'
                            vals['legal_name'] = nome_cliente
                        else:
                            vals['company_type'] = 'person'
                        ie = ''
                        if isinstance(rowValues[5], float):
                            ie = str(int(rowValues[5])).strip()
                        else:
                            ie = rowValues[5].strip()
                        partner = self.env['res.partner'].search([('cnpj_cpf','=',cnpj_cpf)])
                        if partner:
                            comeca_contar = 5
                            continue
                        partner = self.env['res.partner'].search([('name','=',nome)])
                        if partner:
                            comeca_contar = 5
                            continue
                    if comeca_contar == 1 and not rowValues[1]:
                        comeca_contar = 0
                    if comeca_contar == 2:    
                        endereco_values = self.endereco(rowValues[2])
                    
                    #import pudb;pu.db
                    if comeca_contar == 3:
                        vals['phone'] = rowValues[2].strip()
                    
                    if rowValues[1] and comeca_contar > 1 and comeca_contar < 5:
                        if isinstance(rowValues[1], float):
                            comeca_contar = 0
                            grava(vals, ie, cnpj_cpf)
                            vals = {}
"""
"""
                            print ('Importando Cliente ... - %s ...' %(nome))
                            #import pudb;pu.db
                            try:
                                p_id =  client_obj.sudo().create(vals)
                            except:
                                import pudb;pu.db
                                print ('erro aqui %' %(nome))
                            if endereco_values:
                                p_id.write(endereco_values)
                            if ie and len(cnpj_cpf) > 14:
                                uf = p_id.state_id and p_id.state_id.code.lower() or ''
                                res = p_id._validate_ie_param(uf, ie)
                                if res:
                                    p_id.write({'inscr_est': ie})
                                else:
                                    p_id.write({'comment': 'Insc. Estadual: %s' %(ie)})
                            else:
                                if ie:
                                    p_id.write({'rg_fisica': ie})
                            if cnpj_cpf:
                                if len(cnpj_cpf) > 14:
                                    if fiscal.validate_cnpj(cnpj_cpf):
                                        p_id.write({'cnpj_cpf': cnpj_cpf})
                                    else:
                                        p_id.write({'comment': 'CNPJ: %s' %(cnpj_cpf)})
                                else:
                                    if fiscal.validate_cpf(cnpj_cpf):
                                        p_id.write({'cnpj_cpf': cnpj_cpf})
                                    else:
                                        p_id.write({'comment': 'CPF: %s' %(cnpj_cpf)})

                            self.env.cr.commit()
                            vals = {}
"""
"""
                    if comeca_contar == 4 and rowValues[2]:
                        linha = rowValues[2].find('E-mail')
                        email = ''
                        if linha > -1:
                            email = rowValues[2]
                            email = email[linha+7:len(email)].strip()
                            lnh = rowValues[2].find('Contato')
                            if lnh > -1:
                                vals['function'] = rowValues[2][:linha].strip()
                        if linha == -1:
                            vals['function'] = rowValues[2].strip()

                        vals['email'] = email
                        grava(vals, ie, cnpj_cpf)
                        vals = {}
                        
                    comeca_contar += 1    
"""                        
"""
                        partner = self.env['res.partner'].search([('name','=',nome_cliente)],limit=1)
                        if partner:
                            altera = {}
                            if 'cnpj_cpf' in vals:
                                altera['cnpj_cpf']= vals['cnpj_cpf']
                            if 'rg_fisica' in vals:
                                altera['rg_fisica']= vals['rg_fisica']
                            partner.write(altera) 
                            linha = 1
                            vals = {}
                            continue
"""
"""                       
                linha += 1
                conta_registros += 1
                    
        return client_id
"""
