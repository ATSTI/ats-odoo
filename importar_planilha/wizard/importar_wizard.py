# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, _, api
from datetime import datetime, date
from odoo.exceptions import ValidationError
import base64
import tempfile
import time
import xlrd
import re
import os.path
from erpbrasil.base.fiscal import cnpj_cpf, ie


class ImportarWizard(models.TransientModel):
    _name = "importar.wizard"
    _description = "Importar Wizard"

    def _le_registro(self):
        if not self.tipo:
            return True
        arquivo = f"/tmp/registro_{self.tipo}.txt"
        if not (os.path.isfile(arquivo)):
            arq = open(arquivo, "w+")
            if self.tipo == "produto":
                arq.write("c_codigo=0")
                arq.write("\n")
                arq.write("c_nome=1")
                arq.write("\n")
                arq.write("c_ncm=6")
                arq.write("\n")
                arq.write("c_preco_venda=3")
                arq.write("\n")
                arq.write("c_custo=2")
                arq.write("\n")
                arq.write("c_tipo_fiscal=65")
                arq.write("\n")
                arq.write("c_unidade=4")
                arq.write("\n")
                arq.write("c_codbarra=7")
                arq.write("\n")
                arq.write("c_marca=8")
                arq.write("\n")
                arq.write("c_categoria=9")
                arq.write("\n")
            if self.tipo == "cliente" or self.tipo == "fornecedor":
                arq.write("c_ref=0")
                arq.write("\n")
                arq.write("c_name=2")
                arq.write("\n")
                arq.write("c_razao=3")
                arq.write("\n")
                arq.write("c_cnpj_cpf=4")
                arq.write("\n")
                arq.write("c_inscrest=5")
                arq.write("\n")
                arq.write("c_rg=63")
                arq.write("\n")
                arq.write("c_zip=16")
                arq.write("\n")
                arq.write("c_street_name=9") 
                arq.write("\n")
                arq.write("c_street_number=10")
                arq.write("\n")
                arq.write("c_district=11")
                arq.write("\n")
                arq.write("c_street2=13")
                arq.write("\n")
                arq.write("c_company_type=61")
                arq.write("\n")
                arq.write("c_state_id=15")
                arq.write("\n")
                arq.write("c_city_id=12")
                arq.write("\n")
                arq.write("c_phone=17")
                arq.write("\n")
                arq.write("c_mobile=18")
                arq.write("\n")
                arq.write("c_mobile2=19")
                arq.write("\n")
                arq.write("c_email=20")
                arq.write("\n")
                arq.write("c_fiscal_profile_id=62")
                arq.write("\n")
                arq.write("c_nascimento=63")
                arq.write("\n")
                arq.write("c_outros=64")
                arq.write("\n")
            if self.tipo == "dependente":
                arq.write("c_ref=1")
                arq.write("\n")
                arq.write("c_name=2")
                arq.write("\n")
                arq.write("c_razao=2")
                arq.write("\n")
                arq.write("c_cnpj_cpf=68")
                arq.write("\n")
                arq.write("c_inscrest=63")
                arq.write("\n")
                arq.write("c_rg=9")
                arq.write("\n")
                arq.write("c_zip=37")
                arq.write("\n")
                arq.write("c_street_name=30")
                arq.write("\n")
                arq.write("c_street_number=31")
                arq.write("\n")
                arq.write("c_district=33") 
                arq.write("\n")
                arq.write("c_street2=32")
                arq.write("\n")
                arq.write("c_company_type=61")
                arq.write("\n")
                arq.write("c_state_id=34") 
                arq.write("\n")
                arq.write("c_city_id = 33")
                arq.write("\n")
                arq.write("c_phone = 24")
                arq.write("\n")
                arq.write("c_mobile=7")
                arq.write("\n")
                arq.write("c_mobile2=8")
                arq.write("\n")
                arq.write("c_email=29")
                arq.write("\n")
                arq.write("c_fiscal_profile_id=62")
                arq.write("\n")                 
                arq.write("c_resp_financeiro=5") 
                arq.write("\n")
                arq.write("c_birthdate_date=22")
                arq.write("\n")
                arq.write("c_gender=4")
                arq.write("\n")
                arq.write("c_birth_city=23")
                arq.write("\n")
                arq.write("c_birth_state_id=28")
                arq.write("\n")
            arq.close    
        arq = open(arquivo)
        linhas = arq.readlines()
        ln = ''
        for linha in linhas:
            # print(linha)
            ln += f"{linha}"
        self.input_campos = ln
        arq.close

    input_file = fields.Binary('Arquivo', required=False)
    input_campos = fields.Text('Ordem dos Campos')
    tipo = fields.Selection([
            ("produto", "Produto"),
            ("cliente", "Cliente"),
            ("fornecedor", "Fornecedor"),
            ("dependente", "Dependente"),
        ],
        string="Tipo Importação",
    )
    mensagem = fields.Html('Log :', readonly=True)
    inicio = fields.Integer('Linha inicial')
    fim = fields.Integer('Linha final')

    def gravar_campos(self):
        arquivo = f"/tmp/registro_{self.tipo}.txt"
        arq = open(arquivo,"w+")
        arq.write(self.input_campos)
        arq.close

    @api.onchange('tipo')
    def onchange_tipo(self):
        self._le_registro()

    def action_importar_produto(self):
        self.gravar_campos()
        linhas = self.input_campos.split('\n')
        # Colunas
        for linha in linhas:    
            if "c_codigo" in linha:
                c_codigo = int(linha[linha.find('=')+1:])
            if "c_nome" in linha:
                c_nome = int(linha[linha.find('=')+1:])
            if "c_ncm" in linha:
                c_ncm = int(linha[linha.find('=')+1:])
            if "c_preco_venda" in linha:
                c_preco_venda = int(linha[linha.find('=')+1:])
            if "c_custo" in linha:
                c_custo = int(linha[linha.find('=')+1:])
            if "c_tipo_fiscal" in linha:
                c_tipo_fiscal = int(linha[linha.find('=')+1:])
            if "c_tipo" in linha:
                c_tipo = int(linha[linha.find('=')+1:])
            if "c_unidade" in linha:
                c_unidade = int(linha[linha.find('=')+1:])            
            if "c_codbarra" in linha:
                c_codbarra = int(linha[linha.find('=')+1:])
            if "c_marca" in linha:
                c_marca = int(linha[linha.find('=')+1:])
            if "c_categoria" in linha:
                c_categoria = int(linha[linha.find('=')+1:])

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
                        vals['default_code'] = str(cod)
                    descricao = ''
                    if rowValues[c_nome]:
                        descricao = rowValues[c_nome]
                        vals['name'] = rowValues[c_nome]
                    p_id = prod_obj.search([('name', '=', descricao)])
                    if p_id:
                        continue
                    #if descricao:
                    #    print ('Produto: %s' %(descricao))                        

                    # Marca
                    if len(rowValues) > c_marca-1 and rowValues[c_marca]:
                        marca = rowValues[c_marca]
                        mc = self.env["product.brand"]
                        marca_id = mc.search([('name', '=', marca)])
                        if not marca_id:
                            marca_id = mc.create({'name': marca})
                        vals['product_brand_id'] = marca_id.id

                    # Categoria
                    if len(rowValues) > c_categoria-1 and rowValues[c_categoria]:
                        categoria = rowValues[c_categoria]
                        pc = self.env["product.category"]
                        cat_id = pc.search([('name', 'ilike', categoria)])
                        if not cat_id:
                            cat_id = pc.create({'name': categoria, 'parent_id': 1})
                        vals['categ_id'] = cat_id.id

                    if len(rowValues) > c_preco_venda-1 and rowValues[c_preco_venda]:
                        try:
                            vals['lst_price'] = float(rowValues[c_preco_venda])
                        except:
                            pass
                    if len(rowValues) > c_custo-1 and rowValues[c_custo]:
                        try:
                            vals['standard_price'] = float(rowValues[c_custo])
                        except:
                            pass
                    
                    # Tipo Fiscal - esta colocando Produto Revenda
                    vals['fiscal_type'] = '00'
                    vals['type'] = 'product'
                    if len(rowValues) > c_tipo-1 and rowValues[c_tipo]:
                        vals['type'] = rowValues[c_tipo]
                    
                    # UNIDADE
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
                    if rowValues[c_ncm]:
                        ncm = rowValues[c_ncm]
                        if type(ncm) == str:
                            if not len(ncm) == 8:
                                ncm = re.sub('[^0-9]', '', ncm)
                        try:
                            if type(ncm) == float:
                                ncm = str(int(ncm)).zfill(8)
                            ncm = '{}.{}.{}'.format(ncm[:4], ncm[4:6], ncm[6:8])
                            ncm_id = self.env['l10n_br_fiscal.ncm'].search([('code', '=', ncm)])
                            if ncm_id:
                                vals['ncm_id'] = ncm_id.id
                        except:
                            pass

                    vals['invoice_policy'] = 'order'

                    # Se utilizar Ponto de Venda
                    # vals['available_in_pos'] = True

                    # vals['purchase_method'] = 'purchase'

                    if len(rowValues) > c_codbarra-1 and rowValues[c_codbarra] and len(str(rowValues[c_codbarra])) > 7:
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
        return {
            'view_mode': 'form',
            'res_model': 'importar.wizard',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
        }

    def action_importar_cliente(self):
        # Colunas
        self.gravar_campos()
        linhas = self.input_campos.split('\n')
        for linha in linhas:    
            if "c_ref" in linha:
                c_ref = int(linha[linha.find('=')+1:])
            if "c_name" in linha:
                c_name = int(linha[linha.find('=')+1:])
            if "c_razao" in linha:
                c_razao = int(linha[linha.find('=')+1:])
            if "c_cnpj_cpf" in linha:
                c_cnpj_cpf = int(linha[linha.find('=')+1:])
            if "c_inscrest" in linha:
                c_inscrest = int(linha[linha.find('=')+1:])
            if "c_rg" in linha:
                c_rg = int(linha[linha.find('=')+1:])
            if "c_zip" in linha:
                c_zip = int(linha[linha.find('=')+1:])
            if "c_street_name" in linha:
                c_street_name = int(linha[linha.find('=')+1:])
            if "c_street_number" in linha:
                c_street_number = int(linha[linha.find('=')+1:])
            if "c_district" in linha:
                c_district = int(linha[linha.find('=')+1:])
            if "c_street2" in linha:
                c_street2 = int(linha[linha.find('=')+1:])
            if "c_company_type" in linha:
                c_company_type = int(linha[linha.find('=')+1:])
            if "c_state_id" in linha:
                c_state_id = int(linha[linha.find('=')+1:])
            if "c_city_id" in linha:
                c_city_id = int(linha[linha.find('=')+1:])
            if "c_phone" in linha:
                c_phone = int(linha[linha.find('=')+1:])
            if "c_mobile" in linha:
                c_mobile = int(linha[linha.find('=')+1:])
            if "c_mobile2" in linha:
                c_mobile2 = int(linha[linha.find('=')+1:])
            if "c_email" in linha:
                c_email = int(linha[linha.find('=')+1:])
            if "c_nascimento" in linha:
                c_nascimento = int(linha[linha.find('=')+1:])
            if "c_fiscal_profile_id" in linha:
                c_fiscal_profile_id = int(linha[linha.find('=')+1:])
            if "c_outros" in linha:
                c_outros = int(linha[linha.find('=')+1:])
        cli_obj = self.env['res.partner']
        mensagem = ""
        for chain in self:
            file_path = tempfile.gettempdir()+'/file_cli.xls'
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
                    c_id = cli_obj.search([('name', 'ilike', vals['name'])])
                    if c_id:
                        continue
                    if self.tipo == "cliente":
                        vals['customer_rank'] = 1
                    if self.tipo == "fornecedor":
                        vals['supplier_rank'] = 1

                    if 'name' in vals and vals['name']:
                        print ("Cliente/Fornecedor: {}".format(vals['name']))                        
                                                                    
                    if rowValues[c_razao]:
                       vals['legal_name'] = rowValues[c_razao]
                    else:
                       vals['legal_name'] = vals['name']
                    # category = []
                    # category.append((0, 0, [1]))
                    # vals['category_id'] = category
                    if rowValues[c_cnpj_cpf]:
                        cnpj_cpf = rowValues[c_cnpj_cpf]
                        if type(cnpj_cpf) == float:
                            cnpj_cpf = str(int(cnpj_cpf))
                            vals['cnpj_cpf'] = str(int(cnpj_cpf))
                        else:
                            cnpj_cpf = re.sub('[^0-9]', '', cnpj_cpf)
                        if len(cnpj_cpf) > 11:
                            cnpj_cpf = f"{cnpj_cpf[:2]}.{cnpj_cpf[2:5]}.{cnpj_cpf[5:8]}/{cnpj_cpf[8:12]}-{cnpj_cpf[12:14]}"
                        else:
                            cnpj_cpf = f"{cnpj_cpf[:3]}.{cnpj_cpf[3:6]}.{cnpj_cpf[6:9]}-{cnpj_cpf[9:12]}"
                        vals['cnpj_cpf'] = str(cnpj_cpf)


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
                        if type(rowValues[c_street_number]) == str:
                            num = rowValues[c_street_number]
                        else:
                            num = str(int(rowValues[c_street_number]))
                        vals['street_number'] = num
                    if rowValues[c_district]:
                        vals['district'] = rowValues[c_district]
                    if len(rowValues) > c_street2-1 and rowValues[c_street2]:
                        vals['street2'] = rowValues[c_street2]
                    if rowValues[c_phone]:
                        vals['phone'] = rowValues[c_phone]
                    mobile = ''
                    if len(rowValues) > c_mobile and rowValues[c_mobile]:
                        mobile = rowValues[c_mobile]
                    if len(rowValues) > c_mobile2 and rowValues[c_mobile2]:
                        if mobile:
                            mobile += ', '
                        mobile += rowValues[c_mobile2]
                    if mobile:
                        vals['mobile'] = mobile
                    if rowValues[c_email]:
                        vals['email'] = rowValues[c_email]

                    if len(rowValues) > c_nascimento and rowValues[c_nascimento]:
                        n = rowValues[c_nascimento]
                        nasc = f"{n[6:10]}-{n[3:5]}-{n[:2]}"
                        vals['birthdate_date'] = nasc
                    if len(rowValues) > c_outros and rowValues[c_outros]:
                        vals['comment'] = str(rowValues[c_outros])


                    if not 'zip' in vals:
                        vals['country_id'] = 31
                        if rowValues[c_state_id]:
                            uf = self.env['res.country.state'].search([
                                ('code', '=', rowValues[c_state_id]),
                                ('country_id', '=', 31)
                            ])
                            if not uf:
                                uf = self.env['res.country.state'].search([
                                    ('name', '=', rowValues[c_state_id]),
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
                        vals_u = {}
                        if c_id and len(rowValues) > c_company_type-1 and rowValues[c_company_type]:
                            if rowValues[c_company_type] == 'Pessoa Jurídica':
                                vals_u['company_type'] = rowValues[c_company_type]
                                vals_u['ind_final'] = "0"
                                vals_u['fiscal_profile_id'] = 4
                                vals_u['ind_ie_dest'] = "1"
                            if rowValues[c_company_type] == 'Pessoa Física':
                                vals_u['company_type'] = 'person'
                                # Consumidor Final
                                vals_u['ind_final'] = "1"
                                # Nao Contribuinte
                                vals_u['fiscal_profile_id'] = 8
                                vals_u['ind_ie_dest'] = "9"
                        else:
                            if 'cnpj_cpf' in vals and len(vals['cnpj_cpf']) > 14:
                                vals_u['company_type'] = 'company'
                                vals_u['ind_final'] = "0"
                                vals_u['fiscal_profile_id'] = 4
                                vals_u['ind_ie_dest'] = "1"
                            else:
                                vals_u['company_type'] = 'person'
                                # Consumidor Final
                                vals_u['ind_final'] = "1"
                                # Nao Contribuinte
                                vals_u['fiscal_profile_id'] = 8
                                vals_u['ind_ie_dest'] = "9"
                        if len(vals_u):
                            c_id.write(vals_u)
                    except Exception as error:
                        if mensagem == "":
                            mensagem += "Erro cadastro : <br>"
                        if 'name' in vals:
                            mensagem += f"{str(error)} - {vals['name']}"  + "<br>"
                        else:
                            mensagem += str(error)  + "<br>"

                    # vals = {
                    #     'category_id': [(6,0,[1])]
                    # }
                    vals['country_id'] = 31
                    if rowValues[c_state_id] and (not c_id.state_id or not c_id.city_id):
                        uf = self.env['res.country.state'].search([
                            ('code', '=', rowValues[c_state_id]),
                            ('country_id', '=', 31)
                        ])
                        if not uf:
                            uf = self.env['res.country.state'].search([
                                    ('name', '=', rowValues[c_state_id]),
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
                                    vals['city'] = city.name
                    if c_id:
                        c_id.write(vals)
                        conta_registros += 1

                    if len(rowValues) > c_inscrest-1 and rowValues[c_inscrest]:
                        inscrest = rowValues[c_inscrest]
                        vl_ie = {}
                        if type(inscrest) == float:
                            inscrest = str(int(inscrest))
                            vl_ie['inscr_est'] = inscrest
                            vl_ie['ind_ie_dest'] = '1'
                        else:
                            vl_ie['inscr_est'] = inscrest
                            vl_ie['ind_final'] = '1'
                        if c_id.state_id:
                            if len(inscrest) > 13 and c_id.state_id.code == 'MG':
                                inscrest = inscrest[1:len(inscrest)]
                                vl_ie['inscr_est'] = inscrest
                            ie_valido = ie.validar(c_id.state_id.code.lower(), inscrest)
                            if ie_valido:
                                c_id.write(vl_ie)
                            else:
                                inscrest = 'IE: ' + inscrest
                                if c_id.comment:
                                    inscrest = c_id.comment + 'IE: ' + inscrest
                                c_id.write({'comment': inscrest})

                    # if c_id and c_id.zip:
                        # try:
                        #     # c_id.zip_search()
                        #     self.env["l10n_br.zip"].zip_search(c_id)
                        # except:
                        # if not 'city_id' in vals:

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
        self.gravar_campos()
        linhas = self.input_campos.split('\n')
        for linha in linhas:    
            if "c_ref" in linha:
                c_ref = int(linha[linha.find('=')+1:])
            if "c_name" in linha:
                c_name = int(linha[linha.find('=')+1:])
            if "c_razao" in linha:
                c_razao = int(linha[linha.find('=')+1:])
            if "c_cnpj_cpf" in linha:
                c_cnpj_cpf = int(linha[linha.find('=')+1:])
            if "c_inscrest" in linha:
                c_inscrest = int(linha[linha.find('=')+1:])
            if "c_rg" in linha:
                c_rg = int(linha[linha.find('=')+1:])
            if "c_zip" in linha:
                c_zip = int(linha[linha.find('=')+1:])
            if "c_street_name" in linha:
                c_street_name = int(linha[linha.find('=')+1:])
            if "c_street_number" in linha:
                c_street_number = int(linha[linha.find('=')+1:])
            if "c_district" in linha:
                c_district = int(linha[linha.find('=')+1:])
            if "c_street2" in linha:
                c_street2 = int(linha[linha.find('=')+1:])
            if "c_company_type" in linha:
                c_company_type = int(linha[linha.find('=')+1:])
            if "c_state_id" in linha:
                c_state_id = int(linha[linha.find('=')+1:])
            if "c_city_id" in linha:
                c_city_id = int(linha[linha.find('=')+1:])
            if "c_phone" in linha:
                c_phone = int(linha[linha.find('=')+1:])
            if "c_mobile" in linha:
                c_mobile = int(linha[linha.find('=')+1:])
            if "c_mobile2" in linha:
                c_mobile2 = int(linha[linha.find('=')+1:])
            if "c_email" in linha:
                c_email = int(linha[linha.find('=')+1:])
            if "c_fiscal_profile_id" in linha:
                c_fiscal_profile_id = int(linha[linha.find('=')+1:])
            if "c_resp_financeiro" in linha:
                c_resp_financeiro = int(linha[linha.find('=')+1:])
            if "c_birthdate_date" in linha:
                c_birthdate_date = int(linha[linha.find('=')+1:])
            if "c_gender" in linha:
                c_gender = int(linha[linha.find('=')+1:])
            if "c_birth_city" in linha:
                c_birth_city = int(linha[linha.find('=')+1:])
            if "c_birth_state_id" in linha:
                c_birth_state_id = int(linha[linha.find('=')+1:])
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
                    c_id = cli_obj.search([('ref', '=', vals['ref']), ('name', '=', vals['name'])])
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
                            vals['fiscal_profile_id'] = 4
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
