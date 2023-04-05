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
#dest = odoorpc.ODOO('127.0.0.1', port=14069)
dest = odoorpc.ODOO('felicita14.atsti.com.br', port=48069)
# Login
origem.login('felicita_atsti_com_br', 'ats@atsti.com.br', 'a2t00s7')
dest.login('felicita14', 'ats@atsti.com.br', 'a2t00s7')

# odoo_user = odoo.env['res.users']

a_cliente = origem.env['res.partner']
b_cliente = dest.env['res.partner']
# odoo_city = odoo.env['res.state.city']
#odoo_fiscal = odoo.env['br_base.tools.fiscal']

hj = datetime.now()
hj = hj - timedelta(days=5)
hj = datetime.strftime(hj,'%Y-%m-%d %H:%M:%S')


a_prod = origem.env['product.product']
a_pt = origem.env['product.template']
# a_uom = origem.env['product.uom']

b_prod = dest.env['product.product']
b_pt = dest.env['product.template']
b_uom = dest.env['uom.uom']
b_cat = dest.env['product.category']


#import pudb;pu.db
prd_ids = a_prod.search([('default_code', '=', 2317495)])
#prd_ids = a_prod.search([], limit=10,order=prd)
cadastra = 0
for prd in a_prod.browse(prd_ids):
    prod_id = b_prod.search([('name', '=', prd.name)])
    #prod_id = b_prod.search([('default_code', '=', prd.default_code)]) 
    #print ('Codigo : %s , Produto : %s.' % (prd.id, prd.name))
    
    if not prod_id:
        prod_odoo = {}            
        cadastra += 1   
        #print ('id: %s, Codigo : %s ,Categoria :%s , Produto : %s.' % (prd.id, prd.default_code,prd.categ_id.id, prd.name))
        #print ('id: %s, Codigo : %s ,Categoria :%s , Produto : %s.' % (prd.id, prd.default_code,prd.categ_id.name, prd.name))
        #import pudb;pu.db
        cat_id = b_cat.search([('name', 'ilike',prd.categ_id.name)], limit=1)              
        #print ('Codigo : %s ,Categoria :%s , Produto : %s.' % (prd.categ_id.id,prd.categ_id.name, prd.name))
        
        if cat_id:
            prod_odoo['categ_id'] = cat_id[0]   
        
        prod_odoo['name'] = prd.name
        prod_odoo['default_code'] = prd.default_code
        prod_odoo['barcode'] = prd.barcode
        prod_odoo['type'] = prd.type
        prod_odoo['fiscal_type'] = '00'
        prod_odoo['margin'] = prd.margin  
        prod_odoo['qtde_atacado'] = prd.qtde_atacado
        prod_odoo['preco_atacado'] = prd.preco_atacado             
        prod_odoo['icms_origin'] = prd.origin
        prod_odoo['invoice_policy'] = 'order'
        
        uni_id = b_uom.search([('code', 'ilike',prd.uom_id.name)], limit=1)
        #import pudb;pu.db 
        if not uni_id:
            uni_id = b_uom.create({'code': prd.uom_id.name, 'name': prd.uom_id.name, 'category_id': 1})     
        if uni_id:
            prod_odoo['uom_id'] = uni_id[0]
            prod_odoo['uom_po_id'] = uni_id[0]
        
        #import pudb;pu.db
        
        nmc_id = dest.env['l10n_br_fiscal.ncm'].search([('code', 'ilike',prd.fiscal_classification_id.code)])
        #import pudb;pu.db 
        
        if not nmc_id:
            prod_odoo['ncm_id'] = 1
        if nmc_id:
            prod_odoo['ncm_id'] = nmc_id[0]     

        prod_odoo['lst_price'] = prd.lst_price
        prod_odoo['standard_price'] = prd.standard_price       
        
        print ('Categoria :%s , Produto : %s.' % (prd.categ_id.name, prd.name))
        # Descomentar se quiser inserir o produto
        id_prod = b_prod.create(prod_odoo)
  
if cadastra > 0:
    print ('Cadastrado %s produtos' % (str(cadastra)))
else:
    print ('Nenhum cadastro PRODUTO a ser feito.')


