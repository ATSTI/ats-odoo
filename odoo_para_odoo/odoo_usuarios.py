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

a_user = origem.env['res.users']
b_user = dest.env['res.users']


hj = datetime.now()
hj = hj - timedelta(days=5)
hj = datetime.strftime(hj,'%Y-%m-%d %H:%M:%S')

######## IMPORTAR USUARIOS
#import pudb;pu.db
a_todos_user = a_user.search([], limit=30)
#import pudb;pu.db
#a_todos_cli = a_cliente.search([('name', '=', cli.name)])
for user in a_user.browse(a_todos_user): 
    #import pudb;pu.db
    user_id = b_user.search([('name', '=', user.name)])
    if not user_id:
        # INCLUIR
        cli_odoo = {}
       
        if user_id:
            continue
        cli_odoo['user.id'] = user.id
        cli_odoo['user.name'] = user.name
        cli_odoo['user.login'] = user.login
        cli_odoo['user.barcode'] = user.barcode
        cli_odoo['user.email'] = user.email
        #import pudb;pu.db
  
        #print ('Usuario : %s.' % (user.name))
        #b_user.create({'name': user.name, 'login': user.login,'barcode': user.barcode})
        b_user.create({'name': user.name, 'login': user.login , 'email' : user.email})  
        
  
        #abaixo inclui
        id_cli = b_user.create(cli_odoo)


    print ('Codigo : %s , Nome : %s. , email : %s.' % (user.id,user.name,user.email))
