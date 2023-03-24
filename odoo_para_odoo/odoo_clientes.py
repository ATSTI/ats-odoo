# -*- coding: utf-8 -*-

import odoorpc
# import fiscal
import re
from datetime import datetime
from datetime import date
from datetime import timedelta
from unidecode import unidecode
from erpbrasil.base.fiscal import cnpj_cpf
import sys
#reload(sys)
#sys.setdefaultencoding("utf-8")

# CONEXAO ODOO ORIGEM
origem = odoorpc.ODOO('felicita.atsti.com.br', port=48069)

#CONEXAO ODOO DESTINO
# Prepare the connection to the server
#odoo = odoorpc.ODOO('192.168.6.100', port=8069)
dest = odoorpc.ODOO('felicita14.atsti.com.br', port=48069)
#dest = odoorpc.ODOO('127.0.0.1', port=14069)
# Login
origem.login('felicita_atsti_com_br', 'ats@atsti.com.br', 'a2t00s7')
dest.login('felicita14', 'ats@atsti.com.br', 'a2t00s7')

# odoo_user = odoo.env['res.users']

a_cliente = origem.env['res.partner']
b_cliente = dest.env['res.partner']
a_city = dest.env['res.city']
a_tag = dest.env['res.partner.category']
#odoo_city = odoo.env['res.state.city']
#odoo_fiscal = odoo.env['br_base.tools.fiscal']

hj = datetime.now()
hj = hj - timedelta(days=5)
hj = datetime.strftime(hj,'%Y-%m-%d %H:%M:%S')

######## IMPORTAR Clientes
cadastra = 0
#a_todos_cli = a_cliente.search([('id', '=',1671)])
#a_todos_cli = a_cliente.search([], limit=50)
a_todos_cli = a_cliente.search([('id', '>',11499), ('id', '<',11800)], order = "id") # ultimo cliente Rosângela  Simioni  Alves
#import pudb;pu.db
#a_todos_cli = a_cliente.search([('name', '=', cli.name)])
for cli in a_cliente.browse(a_todos_cli): 
    #import pudb;pu.db
    cli_id = b_cliente.search([('name', '=', cli.name)])
    if not cli_id:
        # INCLUIR
        cli_odoo = {}      
        
        cli_odoo['company_type'] = cli.company_type
        tipo = cli.company_type     
          
        #import pudb;pu.db
        
        if cnpj_cpf.validar(cli.cnpj_cpf):
            cli_odoo['cnpj_cpf'] = cli.cnpj_cpf 
        else:
            cli_odoo['comment'] = cli.cnpj_cpf 
        

        # Pegar as ID esta cadastrado (1)CLIENTE e (184)CURSO falta (221)FATURA
        if cli.customer:
            cli_odoo['category_id'] = [(6, 0, [105])]
                     
        if cli.supplier:
            cli_odoo['category_id'] = [(6, 0 , [106])]
        
        #tag = a_tag.search([('name', '=', cli.category_id.name)])
        
        tags = []
        for cat in cli.category_id:
            tag = a_tag.search([('name', '=', cat.name)])
            if tag:
                for vtag in a_tag.browse(tag):
                    tags.append(vtag.id)
                if cli.customer and not 105 in tags:
                    tags.append(105)
                    #cli_odoo['category_id'] = [(6, 0, [1,vtag.id])]
                     
                if cli.supplier and not 106 in tags:
                    tags.append(106)
                    #cli_odoo['category_id'] = [(6, 0 , [2])]
                cli_odoo['category_id'] = [(6, 0 , tags)]
                            
        
       
        
        cli_odoo['ref'] = cli.ref
        cli_odoo['name'] = cli.name
        cli_odoo['legal_name'] = cli.legal_name
        #if cli.cpf_cnpj:
        #    cli_odoo['cnpj_cpf'] = cli.cnpj_cpf
        cli_odoo['inscr_est'] = cli.inscr_est
        cli_odoo['inscr_mun'] = cli.inscr_mun
        #cli_odoo['indicador_ie_dest'] = cli.indicador_ie_dest        
       
        #if tipo == 'person':
        #    cli_odoo['rg'] = cli.cnpj_cpf 
        #import pudb;pu.db

        cli_odoo['zip'] = cli.zip 
        cli_odoo['street'] = cli.street
        cli_odoo['street_number'] = cli.number
        
        cli_odoo['district'] = cli.district
        
        cli_odoo['country_id'] = 31
        cli_odoo['street2'] = cli.street2 
        
        
        city = a_city.search([('name', '=', cli.city_id.name)])
        for vcity in a_city.browse(city):      
              
            cli_odoo['city_id'] = vcity.id        
            cli_odoo['state_id'] = vcity.state_id.id  
       
        
        cli_odoo['phone'] = cli.phone
        cli_odoo['mobile'] = cli.mobile
        cli_odoo['email'] = cli.email
        #cli_odoo['fiscal_profile_id'] = cli.fiscal_profile_id
         
        
        
        #abaixo inclui
        #import pudb;pu.db
        id_cli = b_cliente.create(cli_odoo)
        cadastra += 1 

    print ('Codigo : %s , Nome : %s.' % (cli.id,cli.name))
 

if cadastra > 0:
    print (' Cadastrado %s clientes' % (str(cadastra)))
else:
    print ('Nenhum cadastro Cliente a ser feito.')


        

