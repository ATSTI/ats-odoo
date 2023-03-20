# -*- coding: utf-8 -*-

import odoorpc
# import fiscal
import re
from datetime import datetime
from datetime import date
from datetime import timedelta
from unidecode import unidecode
import sys
#reload(sys)
#sys.setdefaultencoding("utf-8")

# CONEXAO ODOO ORIGEM
origem = odoorpc.ODOO('felicita.atsti.com.br', port=48069)

#CONEXAO ODOO DESTINO
# Prepare the connection to the server
#odoo = odoorpc.ODOO('192.168.6.100', port=8069)
#dest = odoorpc.ODOO('felicita14.atsti.com.br', port=48069)
dest = odoorpc.ODOO('127.0.0.1', port=14069)
# Login
origem.login('felicita_atsti_com_br', 'ats@atsti.com.br', 'a2t00s7')
dest.login('felicita', 'ats@atsti.com.br', 'a2t00s7')

# odoo_user = odoo.env['res.users']

a_cliente = origem.env['res.partner']
b_cliente = dest.env['res.partner']

#odoo_city = odoo.env['res.state.city']
#odoo_fiscal = odoo.env['br_base.tools.fiscal']

hj = datetime.now()
hj = hj - timedelta(days=5)
hj = datetime.strftime(hj,'%Y-%m-%d %H:%M:%S')

######## IMPORTAR Clientes
cadastra = 0
a_todos_cli = a_cliente.search([('id', '=', 9519)])
#a_todos_cli = a_cliente.search([], limit=2)
#import pudb;pu.db
#a_todos_cli = a_cliente.search([('name', '=', cli.name)])
for cli in a_cliente.browse(a_todos_cli): 
    import pudb;pu.db
    cli_id = b_cliente.search([('name', '=', cli.name)])
    if not cli_id:
        # INCLUIR
        cli_odoo = {}
        '''
        cli_odoo['credit_limit'] = cli.credit_limit
        cli_odoo['user_id'] = cli.user_id.id
        
        cli_odoo['comment'] = cli.comment
        '''
        
        cli_odoo['company_type'] = cli.company_type
        tipo = cli.company_type
        cli_odoo['ref'] = cli.ref
        cli_odoo['name'] = cli.name
        cli_odoo['legal_name'] = cli.legal_name
        if cli.cpf_cnpj:
            cli_odoo['cnpj_cpf'] = cli.cnpj_cpf
        cli_odoo['inscr_est'] = cli.inscr_est
        cli_odoo['inscr_mun'] = cli.inscr_mun
        #cli_odoo['indicador_ie_dest'] = cli.indicador_ie_dest
        if tipo == 'person':
            cli_odoo['rg'] = cli.rg    
        cli_odoo['zip'] = cli.zip 
        cli_odoo['street'] = cli.street
        cli_odoo['street_number'] = cli.number
        
        cli_odoo['district'] = cli.district
        
        cli_odoo['country_id'] = cli.country_id.id
        cli_odoo['street2'] = cli.street2 
        cli_odoo['state_id'] = cli.state_id.id
        
        cli_odoo['city_id'] = cli.city_id.id
        
        cli_odoo['phone'] = cli.phone
        cli_odoo['mobile'] = cli.mobile
        cli_odoo['email'] = cli.email
        #cli_odoo['fiscal_profile_id'] = cli.fiscal_profile_id
         
        
        
        #abaixo inclui
        #id_cli = b_cliente.create(cli_odoo)
        cadastra += 1 

    print ('Codigo : %s , Nome : %s.' % (cli.id,cli.name))
    '''
    if row[24]:
        cod_ibge = row[24][2:]
        cod_ibge = cod_ibge.replace('-','')
        city_ids = odoo_city.search([('ibge_code', '=', cod_ibge)])
    city = odoo_city.browse(city_ids)

    fone = ('(%s) %s') % (str(row[20]), str(row[14]))
    fone1 = ('(%s) %s') % (str(row[21]), str(row[15]))

    cliente = ''
    if row[1]:
        cliente = unidecode(str(row[1]))
        #cliente = (u'%s') % (cliente.decode('latin-1'))
    razao = ''
    if row[2]:
       razao = unidecode(str(row[2]))
       #razao = (u'%s') %(razao.decode('latin-1'))

    #import pudb;pu.db
    if row[5]:
        check_ie = True
        ie = str(row[5])
        if str(row[5]) == 'ISENTA' or str(row[5]) == 'INSENTO':
            ie = 'ISENTO'
        uf = city.state_id.code.lower()
        try:
            validate = getattr(fiscal, 'validate_ie_%s' % uf)
            if not validate(ie):
                check_ie = False
        except AttributeError:
            if not fiscal.validate_ie_param(uf, ie):
                check_ie = False
        if not check_ie:
            cli_odoo['vat'] = 'IE: ' + str(ie)
        else:
            cli_odoo['inscr_est'] = str(ie)
        #elif city:
        #    ie = str(row[5])
        #    #import pudb;pu.db
        #    uf = str(city.state_id.code.lower())
            #try:
            #    valida = fiscal.validate_ie_param(uf, ie)
            #except:
            #    ie = ''    
            #if uf == 'to':
            #    valida = fiscal.validate_ie_to(ie)
            #if empresa and not valida:
            #    #  validate_cnpj(vals['cnpj_cpf']):
            #    #anotacoes = ' CNPJ Invalido : %s \n' %(vals['cnpj_cpf'])
            #    #vals['cnpj_cpf'] = ''
                #    ie = ''
        bairr = ''
        if row[9]:
            bairr = unidecode(str(row[9]))

        obs = ''
        if row[26]:
            obs = unidecode(str(row[26]))
            #obs = (u'%s') % (obs.decode('latin-1'))

        endereco = unidecode(str(row[8]))
        if row[10]:
            cli_odoo['street2'] = unidecode(str(row[10]))

        print (' Cadastrando Titular: %s - %s - %s - %s ' % (str(row[0]), str(row[4]), str(row[5]), row[1]))
        cep = ''
        if row[13]:
            cep = '%s%s' %(row[13][:5], row[13][5:])
        cli_odoo['ref'] = str(row[0])
        cli_odoo['name'] = cliente
        cli_odoo['legal_name'] = razao


        cli_odoo['comment'] = obs
        cli_odoo['street'] = endereco

        cli_odoo['zip'] = cep
        cli_odoo['city_id'] = city.id
        cli_odoo['state_id'] = city.state_id.id
        cli_odoo['country_id'] = city.state_id.country_id.id
        cli_odoo['district'] = str(bairr)
        cli_odoo['phone'] = str(fone)
        cli_odoo['mobile'] = str(fone1)
        cli_odoo['email'] = str(row[17])
        cli_odoo['number'] = str(row[23])
        cli_odoo['property_account_position_id'] = 1

        cli_odoo['is_company'] = empresa
        
        #abaixo inclui 
        id_cli = odoo_cliente.create(cli_odoo)    

        

'''

if cadastra > 0:
    print (' Cadastrado %s clientes' % (str(cadastra)))
else:
    print ('Nenhum cadastro Cliente a ser feito.')

######## FIM DO IMPORTA CLIENTE
        

