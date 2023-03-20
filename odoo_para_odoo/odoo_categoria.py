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


a_prod = origem.env['product.category']
#a_pt = origem.env['product.template']
# a_uom = origem.env['uom.uom']

b_prod = dest.env['product.category']
#b_pt = dest.env['product.template']
# b_uom = dest.env['uom.uom']
#import pudb;pu.db
#cat_ids = a_prod.search([('parent_id','=',False)], limit=200)  #Rodar na Primira vez assim
cat_ids = a_prod.search([], limit=200)                          #Rodar pela segunda vez assim
for cat in a_prod.browse(cat_ids):
    cat_id = b_prod.search([('name','=', cat.name)])
    #print ('Codigo : %s , Categoria : %s.' % (cat.id, cat.name))
    
    if not cat_id:
        prod_odoo = {}            
        # if row[7]:
        #     marca = unidecode(str(row[7]))
        #     marca_id = odoo_marca.search([('name', '=', marca)])
        #     prod_odoo['product_brand_id'] = marca_id[0]
        prod_odoo['name'] = cat.name
        #if not cat.parent_id:
        #    continue
        if cat.parent_id: 
            parent_id = b_prod.search([('name','=', cat.parent_id.name)])   
            #print ('Codigo : %s , Categoria : %s.' % (cat.id, cat.name))
            prod_odoo['parent_id'] = parent_id[0]
        #prod_odoo['default_code'] = cat.default_code
        #prod_odoo['barcode'] = prd.barcode
        # prod_odoo['type'] = 'product'
        # prod_odoo['fiscal_category_id'] = 1      
        #prod_odoo['origin'] = str(row[9])
        #print ('Codigo : %s , Categoria : %s.' % (cat.id, cat.name))
        b_prod.create(prod_odoo)
        # prdid = odoo_prod.browse(id_prod)
        # odoo_pt.write(prdid.product_tmpl_id.id,{
        #     'default_code': str(row[0]),
        #     'standard_price': price,
        # })
    else:
        
        prod_odoo = {}
        prod_odoo['name'] = cat.name
        #if not cat.parent_id:
        #    continue
        if cat.parent_id: 
            #import pudb;pu.db
            parent_id = b_prod.search([('name','=', cat.parent_id.name)])
            if parent_id:   
                print ('Codigo : %s , Categoria : %s.' % (cat.id, cat.name))
                prod_odoo['parent_id'] = parent_id[0]
                cat_b = b_prod.browse(cat_id)
                b_prod.write(cat_b.id,{'parent_id': parent_id})
        #     'default_code': str(row[0]),
        #     'standard_price': price,
        
# if cadastra > 0:
#     print (' Cadastrado %s produtos' % (str(cadastra)))
# else:
#     print ('Nenhum cadastro PRODUTO a ser feito.')

