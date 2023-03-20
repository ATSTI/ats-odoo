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
dest = odoorpc.ODOO('127.0.0.1', port=59069)
# Login
origem.login('felicita_atsti_com_br', 'ats@atsti.com.br', 'a2t00s7')
dest.login('felicita14', 'ats@atsti.com.br', 'a2t00s7')

# odoo_user = odoo.env['res.users']

#a_cliente = origem.env['res.partner']
#b_cliente = dest.env['res.partner']
# odoo_city = odoo.env['res.state.city']
#odoo_fiscal = odoo.env['br_base.tools.fiscal']

hj = datetime.now()
hj = hj - timedelta(days=5)
hj = datetime.strftime(hj,'%Y-%m-%d %H:%M:%S')


#a_prod = origem.env['product.category']
#a_pt = origem.env['product.template']
a_uom = origem.env['product.uom']

#b_prod = dest.env['product.category']
#b_pt = dest.env['product.template']
b_uom = dest.env['uom.uom']
#import pudb;pu.db
#cat_ids = a_uom.search([('uom_id','=',False)], limit=200)   
uni_ids = a_uom.search([])                         
for uni in a_uom.browse(uni_ids):
    uni_id = b_uom.search([('name','=', uni.name)])
    #print ('Codigo : %s , Unidade de Medida : %s.' % (uni.id, uni.name))
    
    if not uni_id:
        prod_odoo = {}            
        prod_odoo['name'] = uni.name 
        if uni_id: 
            uni_id = b_uom.search([('name','=', uni.name)])   
        print ('Codigo : %s , Unidade de Medida : %s.' % (uni.id, uni.name))
        prod_odoo['id'] = uni.id
        prod_odoo['name'] = uni.name
        prod_odoo['category_id'] = uni.category_id.id
        prod_odoo['uom_type'] = uni.uom_type
        # prod_odoo['fiscal_category_id'] = 1      
        #prod_odoo['origin'] = str(row[9])

        #b_prod.create(prod_odoo)

# if cadastra > 0:
#     print (' Cadastrado %s produtos' % (str(cadastra)))
# else:
#     print ('Nenhum cadastro PRODUTO a ser feito.')



