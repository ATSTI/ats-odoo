# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, _, api
from datetime import datetime, date
from odoo.exceptions import ValidationError
import base64
import tempfile
import time
import xlrd
import re


class ImportarWizard(models.TransientModel):
    _name = "importar.wizard"
    _description = "Importar Wizard"


    input_file = fields.Binary('Arquivo', required=False)
    mensagem = fields.Html('Log :', readonly=True)
    inicio = fields.Integer('Linha inicial')
    fim = fields.Integer('Linha final')

    def action_importar_produto(self):
        # Colunas
        c_codigo = 1
        c_nome = 2
        c_ncm = 17
        c_preco_venda = 6
        c_custo = 4
        # Materia Prima, Mercadoria Revenda
        c_tipo_fiscal = 6
        c_unidade = 11
        c_codbarra = 13
        mensagem = ""
        prod_obj = self.env['product.product']
        #uom_obj = self.env['product.uom']
        tmpl_obj = self.env['product.template']
        for chain in self:
            file_path = tempfile.gettempdir()+'/file.xls'
            data = base64.decodebytes(chain.input_file)
            f = open(file_path,'wb')
            f.write(data)
            f.close()
            book = xlrd.open_workbook(file_path)
            first_sheet = book.sheet_by_index(0)
            conta_registros = 0
            for rownum in range(first_sheet.nrows):                                                                                                       
                rowValues = first_sheet.row_values(rownum)
                if rownum > self.inicio and rownum < self.fim:
                    vals = {}
                    if rowValues[c_codigo]:
                        cod = rowValues[c_codigo]
                        vals['default_code'] = str(int(cod))
                    descricao = ''
                    if rowValues[c_nome]:
                        descricao = rowValues[c_nome]
                        vals['name'] = rowValues[c_nome]
                    p_id = prod_obj.search([('name', '=', descricao)])
                    if p_id:
                        continue
                    if descricao:
                        print ('Produto: %s' %(descricao))                        
                                                                    
                    if rowValues[c_preco_venda]:
                        try:
                            vals['lst_price'] = float(rowValues[c_preco_venda])
                        except:
                            pass
                    if rowValues[c_custo]:
                        try:
                            vals['standard_price'] = float(rowValues[c_custo])
                        except:
                            pass
                    
                    # Tipo Fiscal - esta colocando Produto Revenda
                    vals['fiscal_type'] = '00'
                    
                    # UNIDADE
                    # import pudb;pu.db 
                    # if rowValues[c_unidade] and type(rowValues[c_unidade]) == str:
                    #     d_uom = self.env['uom.uom']
                    #     uni_id = d_uom.search([('code', 'ilike', rowValues[c_unidade])], limit=1)
                    #     if not uni_id:
                    #         uni_id = d_uom.create({'code': rowValues[c_unidade], 'name': rowValues[c_unidade], 'category_id': 1})     
                    #     else:
                    #         vals['uom_id'] = uni_id.id
                    #         vals['uom_po_id'] = uni_id.id

                    # NCM
                    # if vals['default_code'] == '2000000000275':
                    #     import pudb;pu.db
                    if rowValues[c_ncm]:
                        ncm = rowValues[c_ncm]
                        if type(ncm) == str:
                            if not len(ncm) == 8:
                                ncm = re.sub('[^0-9]', '', ncm)
                        try:
                            if type(ncm) == float:
                                ncm = str(int(ncm))
                            ncm = '{}.{}.{}'.format(ncm[:4], ncm[4:6], ncm[6:8])
                            ncm_id = self.env['l10n_br_fiscal.ncm'].search([('code', '=', ncm)])
                            if ncm_id:
                                vals['ncm_id'] = ncm_id.id
                        except:
                            pass

                    vals['invoice_policy'] = 'order'

                    # Se utilizar Ponto de Venda
                    # vals['available_in_pos'] = True

                    vals['purchase_method'] = 'purchase'

                    if rowValues[c_codbarra] and len(str(rowValues[c_codbarra])) > 7:
                        bcod = str(rowValues[c_codbarra])
                        if type(bcod) == str:
                            try:
                                bcod = str(int(bcod))
                                bcod = re.sub('[^0-9]', '', bcod)
                                if len(bcod) > 7:
                                    if type(bcod) == float:
                                        bcod = str(int(bcod))
                                    vals['barcode'] = str
                            except:
                                pass

                    try:
                        p_id =  prod_obj.create(vals)
                    except Exception as error:
                        if mensagem == "":
                            mensagem += "Erro cadastro : <br>"
                        mensagem += str(error) + "<br>"
                        if 'name' in vals:
                            mensagem += f"{vals['name']}<br>"

                    conta_registros += 1

            mensagem += f"TOTAL DE REGISTROS INCLUIDOS : {str(conta_registros)}"
            self.write({'mensagem': mensagem})


    def action_importar_cliente(self):
        # Colunas
        c_ref = 0
        c_name = 2
        c_razao = 3
        c_cnpj_cpf = 4
        c_inscrest = 5
        c_rg = 63
        c_zip = 16
        c_street_name = 9
        c_street_number = 10
        c_district = 11
        # complemento
        c_street2 = 13
        # person / company
        c_company_type = 61
        c_state_id = 15
        c_city_id = 12
        # c_country_id = 14
        c_phone = 17
        c_mobile = 18
        c_mobile2 = 19
        c_email = 20
        # Simples-0, Contribuinte-3, Não contribuinte-4, isento-5
        c_fiscal_profile_id = 62

        cli_obj = self.env['res.partner']
        mensagem = ""
        for chain in self:
            file_path = tempfile.gettempdir()+'/file.xls'
            data = base64.decodebytes(chain.input_file)
            f = open(file_path,'wb')
            f.write(data)
            f.close()
            book = xlrd.open_workbook(file_path)
            first_sheet = book.sheet_by_index(0)
            conta_registros = 0
            
            for rownum in range(first_sheet.nrows):                                                                                                       
                rowValues = first_sheet.row_values(rownum)
                if rownum > self.inicio and rownum < self.fim:
                    vals = {}
                    cod = 0
                    cnpj_cpf = ""
                    if rowValues[c_ref]:
                        cod = rowValues[c_ref]
                        if type(cod) == float:
                            vals['ref'] = str(int(cod))
                        else:
                            vals['ref'] = cod
                    else:
                        # REF e obrigatorio
                        if mensagem == "":
                            mensagem += "Sem o campo codigo : <br>"
                        mensagem += f"{vals['name']}<br>"                        
                        continue
                    # if cod and cod == '0000518':
                    if rowValues[c_name]:
                        vals['name'] = rowValues[c_name]
                    c_id = cli_obj.search([('ref', '=', vals['ref'])])
                    if c_id:
                        continue

                    if vals['name']:
                        print ("Cliente: {}".format(vals['name']))                        
                                                                    
                    if rowValues[c_razao]:
                       vals['legal_name'] = rowValues[c_razao]
                    else:
                       vals['legal_name'] = vals['name']
                    # import pudb;pu.db
                    # category = []
                    # category.append((0, 0, [1]))
                    # vals['category_id'] = category

                    if rowValues[c_cnpj_cpf]:
                        cnpj_cpf = rowValues[c_cnpj_cpf]
                        if type(cnpj_cpf) == float:
                            vals['cnpj_cpf'] = str(int(cnpj_cpf))
                        else:
                            cnpj_cpf = re.sub('[^0-9]', '', cnpj_cpf)
                        if len(cnpj_cpf) > 11:
                            cnpj_cpf = f"{cnpj_cpf[:2]}.{cnpj_cpf[2:5]}.{cnpj_cpf[5:8]}/{cnpj_cpf[8:12]}-{cnpj_cpf[12:14]}"
                        else:
                            cnpj_cpf = f"{cnpj_cpf[:3]}.{cnpj_cpf[3:6]}.{cnpj_cpf[6:9]}-{cnpj_cpf[9:12]}"
                        vals['cnpj_cpf'] = str(cnpj_cpf)

                    if len(rowValues) > c_inscrest-1 and rowValues[c_inscrest]:
                        inscrest = rowValues[c_inscrest]
                        if type(inscrest) == float:
                            vals['inscr_est'] = str(int(inscrest))
                        else:
                            vals['inscr_est'] = inscrest

                    if len(rowValues) > c_rg-1 and rowValues[c_rg]:
                        rg = rowValues[c_rg]
                        if type(rg) == float:
                            vals['rg'] = str(int(rg))
                        else:
                            vals['rg'] = str(rg)

                    if rowValues[c_zip]:
                        cep = rowValues[c_zip]
                        if type(cep) == float:
                            cep = str(int(cep))
                        if len(cep) > 8:
                            cep = re.sub('[^0-9]', '', cep)
                        cep = f"{cep[:5]}-{cep[5:8]}"
                        vals['zip'] = cep

                    if rowValues[c_street_name]:
                        vals['street_name'] = rowValues[c_street_name]
                    if rowValues[c_street_number]:
                        vals['street_number'] = rowValues[c_street_number]
                    if rowValues[c_district]:
                        vals['district'] = rowValues[c_district]
                    if len(rowValues) > c_street2-1 and rowValues[c_street2]:
                        vals['street2'] = rowValues[c_street2]
                    if rowValues[c_phone]:
                        vals['phone'] = rowValues[c_phone]
                    if rowValues[c_mobile] or rowValues[c_mobile2]:
                        vals['mobile'] = rowValues[c_mobile] or rowValues[c_mobile2]
                    if rowValues[c_email]:
                        vals['email'] = rowValues[c_email]

                    if len(rowValues) > c_company_type-1 and rowValues[c_company_type]:
                        vals['company_type'] = rowValues[c_company_type]
                    else:
                        if 'cnpj_cpf' in vals and len(vals['cnpj_cpf']) > 14:
                            vals['company_type'] = 'company'
                            vals['ind_final'] = "0"
                            vals['fiscal_profile_id'] = 8
                            vals['ind_ie_dest'] = "1"
                        else:
                            vals['company_type'] = 'person'
                            # Consumidor Final
                            vals['ind_final'] = "1"
                            # Nao Contribuinte
                            vals['fiscal_profile_id'] = 8
                            vals['ind_ie_dest'] = "9"

                    if not 'zip' in vals:
                        vals['country_id'] = 31
                        if rowValues[c_state_id]:
                            uf = self.env['res.country.state'].search([
                                ('code', '=', rowValues[c_state_id]),
                                ('country_id', '=', 31)
                            ])
                            if uf:
                                vals['state_id'] = uf.id
                                if rowValues[c_city_id]:
                                    city = self.env['res.city'].search([
                                        ('name', '=', rowValues[c_city_id]),
                                        ('country_id', '=', 31),
                                        ('state_id', '=', uf.id),
                                    ])
                                    if city:
                                        vals['city_id'] = city.id

                    # if len(rowValues) > c_fiscal_profile_id-1 and rowValues[c_fiscal_profile_id]:
                    #     vals['fiscal_profile_id'] = rowValues[c_fiscal_profile_id]
                    # else:
                    #     # Nao Contribuinte
                    #     vals['fiscal_profile_id'] = 8

                    try:
                        c_id =  cli_obj.create(vals)
                    except Exception as error:
                        if mensagem == "":
                            mensagem += "Erro cadastro : <br>"
                        if 'name' in vals:
                            mensagem += f"{str(error)} - {vals['name']}"  + "<br>"
                        else:
                            mensagem += str(error)  + "<br>"
                    vals = {
                        'category_id': [(6,0,[1])]
                    }
                    # if c_id and c_id.zip:
                        # try:
                        #     # c_id.zip_search()
                        #     self.env["l10n_br.zip"].zip_search(c_id)
                        # except:
                        # if not 'city_id' in vals:
                    vals['country_id'] = 31
                    if rowValues[c_state_id]:
                        uf = self.env['res.country.state'].search([
                            ('code', '=', rowValues[c_state_id]),
                            ('country_id', '=', 31)
                        ])
                        if uf:
                            vals['state_id'] = uf.id
                            if rowValues[c_city_id]:
                                city = self.env['res.city'].search([
                                    ('name', '=', rowValues[c_city_id]),
                                    ('country_id', '=', 31),
                                    ('state_id', '=', uf.id),
                                ])
                                if city:
                                    vals['city_id'] = city.id
                    if c_id:
                        c_id.write(vals)
                        conta_registros += 1

            mensagem += 'TOTAL DE REGISTROS INCLUIDOS : {}'.format(str(conta_registros))
            self.write({'mensagem': mensagem})

        return {
            'view_mode': 'form',
            'res_model': 'importar.wizard',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
        }

    def action_importar_dependente(self):
        # Colunas
        c_ref = 1
        c_name = 2
        c_razao = 2
        c_cnpj_cpf = 68
        c_inscrest = 63
        c_rg = 9
        c_zip = 37
        c_street_name = 30
        c_street_number = 31
        c_district = 33
        # complemento
        c_street2 = 32
        # person / company
        c_company_type = 61
        c_state_id = 34
        c_city_id = 33
        # c_country_id = 14
        c_phone = 24
        c_mobile = 7
        c_mobile2 = 8
        c_email = 29
        # Simples-0, Contribuinte-3, Não contribuinte-4, isento-5
        c_fiscal_profile_id = 62
        c_resp_financeiro = 5
        # nascimento : Data, Local, Estadao, Pais e Sexo
        c_birthdate_date = 22
        c_gender = 4
        c_birth_city = 23
        c_birth_state_id = 28 

        cli_obj = self.env['res.partner']
        mensagem = ""
        for chain in self:
            file_path = tempfile.gettempdir()+'/file.xls'
            data = base64.decodebytes(chain.input_file)
            f = open(file_path,'wb')
            f.write(data)
            f.close()
            book = xlrd.open_workbook(file_path)
            first_sheet = book.sheet_by_index(0)
            conta_registros = 0

            for rownum in range(first_sheet.nrows):                                                                                                       
                rowValues = first_sheet.row_values(rownum)
                if rownum > self.inicio and rownum < self.fim:
                    vals = {}
                    cod = 0
                    cnpj_cpf = ""
                    if rowValues[c_ref]:
                        cod = rowValues[c_ref]
                        if type(cod) == float:
                            vals['ref'] = str(int(cod))
                        else:
                            vals['ref'] = cod
                    else:
                        # REF e obrigatorio
                        if mensagem == "":
                            mensagem += "Sem o campo codigo : <br>"
                        mensagem += f"{vals['name']}<br>"                        
                        continue
                    # if cod and cod == '0000518':
                    if rowValues[c_name]:
                        vals['name'] = rowValues[c_name]
                    resp_financeiro = cli_obj.search([('name', '=', rowValues[c_resp_financeiro])], limit=1)
                    c_id = cli_obj.search([('ref', '=', vals['ref'])])
                    if c_id or not resp_financeiro:
                        continue
     
                    if resp_financeiro:
                        vals['parent_id'] = resp_financeiro.id
                    if vals['name']:
                        print ("Cliente: {}".format(vals['name']))                        
                                                                    
                    if rowValues[c_razao]:
                       vals['legal_name'] = rowValues[c_razao]
                    else:
                       vals['legal_name'] = vals['name']

                    if rowValues[c_birthdate_date]:
                       vals['birthdate_date'] = datetime(*xlrd.xldate_as_tuple(rowValues[c_birthdate_date], book.datemode))

                    if rowValues[c_gender]:
                        if rowValues[c_gender] == 'Feminino':
                            vals['gender'] = 'female'
                        else:
                            vals['gender'] = 'male'

                    if rowValues[c_birth_city]:
                       vals['birth_city'] = rowValues[c_birth_city]

                    if rowValues[c_birth_state_id]:
                        uf = self.env['res.country.state'].search([
                            ('code', '=', rowValues[c_birth_state_id]),
                            ('country_id', '=', 31)
                        ])
                        if uf:
                            vals['birth_state_id'] = uf.id
                        vals['birth_country_id'] = 31

                    if len(rowValues) > c_cnpj_cpf-1 and rowValues[c_cnpj_cpf]:
                        cnpj_cpf = rowValues[c_cnpj_cpf]
                        if type(cnpj_cpf) == float:
                            vals['cnpj_cpf'] = str(int(cnpj_cpf))
                        else:
                            cnpj_cpf = re.sub('[^0-9]', '', cnpj_cpf)
                        if len(cnpj_cpf) > 11:
                            cnpj_cpf = f"{cnpj_cpf[:2]}.{cnpj_cpf[2:5]}.{cnpj_cpf[5:8]}/{cnpj_cpf[8:12]}-{cnpj_cpf[12:14]}"
                        else:
                            cnpj_cpf = f"{cnpj_cpf[:3]}.{cnpj_cpf[3:6]}.{cnpj_cpf[6:9]}-{cnpj_cpf[9:12]}"
                        vals['cnpj_cpf'] = str(cnpj_cpf)

                    if len(rowValues) > c_inscrest-1 and rowValues[c_inscrest]:
                        inscrest = rowValues[c_inscrest]
                        if type(inscrest) == float:
                            vals['inscr_est'] = str(int(inscrest))
                        else:
                            vals['inscr_est'] = inscrest

                    if len(rowValues) > c_rg-1 and rowValues[c_rg]:
                        rg = rowValues[c_rg]
                        if type(rg) == float:
                            vals['rg'] = str(int(rg))
                        else:
                            vals['rg'] = str(rg)

                    if rowValues[c_zip]:
                        cep = rowValues[c_zip]
                        if type(cep) == float:
                            cep = str(int(cep))
                        if len(cep) > 8:
                            cep = re.sub('[^0-9]', '', cep)
                        cep = f"{cep[:5]}-{cep[5:8]}"
                        vals['zip'] = cep

                    if rowValues[c_street_name]:
                        vals['street_name'] = rowValues[c_street_name]
                    if rowValues[c_street_number]:
                        vals['street_number'] = rowValues[c_street_number]
                    if rowValues[c_district]:
                        vals['district'] = rowValues[c_district]
                    if len(rowValues) > c_street2-1 and rowValues[c_street2]:
                        vals['street2'] = rowValues[c_street2]
                    if rowValues[c_phone]:
                        vals['phone'] = rowValues[c_phone]
                    if rowValues[c_mobile] or rowValues[c_mobile2]:
                        vals['mobile'] = rowValues[c_mobile] or rowValues[c_mobile2]
                    if rowValues[c_email]:
                        vals['email'] = rowValues[c_email]

                    vals['company_type'] = 'person'
                    if len(rowValues) > c_company_type-1 and rowValues[c_company_type]:
                        vals['company_type'] = rowValues[c_company_type]
                    else:
                        if 'cnpj_cpf' in vals and len(vals['cnpj_cpf']) > 14:
                            vals['company_type'] = 'company'
                            vals['ind_final'] = "0"
                            vals['fiscal_profile_id'] = 8
                            vals['ind_ie_dest'] = "1"
                        else:
                            vals['company_type'] = 'person'
                            # Consumidor Final
                            vals['ind_final'] = "1"
                            # Nao Contribuinte
                            vals['fiscal_profile_id'] = 8
                            vals['ind_ie_dest'] = "9"

                    if not 'zip' in vals:
                        vals['country_id'] = 31
                        if rowValues[c_state_id]:
                            uf = self.env['res.country.state'].search([
                                ('code', '=', rowValues[c_state_id]),
                                ('country_id', '=', 31)
                            ])
                            if uf:
                                vals['state_id'] = uf.id
                                if rowValues[c_city_id]:
                                    city = self.env['res.city'].search([
                                        ('name', '=', rowValues[c_city_id]),
                                        ('country_id', '=', 31),
                                        ('state_id', '=', uf.id),
                                    ])
                                    if city:
                                        vals['city_id'] = city.id

                    # if len(rowValues) > c_fiscal_profile_id-1 and rowValues[c_fiscal_profile_id]:
                    #     vals['fiscal_profile_id'] = rowValues[c_fiscal_profile_id]
                    # else:
                    #     # Nao Contribuinte
                    #     vals['fiscal_profile_id'] = 8

                    try:
                        c_id =  cli_obj.create(vals)
                    except Exception as error:
                        if mensagem == "":
                            mensagem += "Erro cadastro : <br>"
                        if 'name' in vals:
                            mensagem += f"{str(error)} - {vals['name']}"  + "<br>"
                        else:
                            mensagem += str(error)  + "<br>"

                    vals = {
                        'category_id': [(6,0,[2])]
                    }
                    # if c_id and c_id.zip:
                        # try:
                        #     c_id.zip_search()
                        # except:                    
                    vals['country_id'] = 31
                    if rowValues[c_state_id]:
                        uf = self.env['res.country.state'].search([
                            ('code', '=', rowValues[c_state_id]),
                            ('country_id', '=', 31)
                        ])
                        if uf:
                            vals['state_id'] = uf.id
                            if rowValues[c_city_id]:
                                city = self.env['res.city'].search([
                                    ('name', '=', rowValues[c_city_id]),
                                    ('country_id', '=', 31),
                                    ('state_id', '=', uf.id),
                                ])
                                if city:
                                    vals['city_id'] = city.id
                    if c_id:
                        c_id.write(vals)
                    conta_registros += 1

            mensagem += 'TOTAL DE REGISTROS INCLUIDOS : {}'.format(str(conta_registros))
            self.write({'mensagem': mensagem})

        return {
            'view_mode': 'form',
            'res_model': 'importar.wizard',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
        }