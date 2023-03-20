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
dest = odoorpc.ODOO('127.0.0.1', port=14069)
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
prd_ids = a_prod.search([], offset=0,limit=1, order = "default_code" )


#prd_ids = a_prod.search([], limit=10,order=prd)
cadastra = 0
for prd_a in a_prod.browse(prd_ids):
    prod_id = b_prod.search([('barcode', '=', prd_a.barcode)])    
    
    if not prd_a.barcode:
    continue
    
    prd_b = b_prod.browse(prod_id)
    vals = {}
    
    
    if prd_b.name != prd_a.name:
        #vals['id'] = prd_ids[0] 
        vals['name'] = prd_a.name
        vals['lst_price'] = prd_a.lst_price
        vals['standard_price'] = prd_a.standard_price 
        vals['margin'] = prd_a.margin  
        vals['qtde_atacado'] = prd_a.qtde_atacado
        vals['preco_atacado'] = prd_a.preco_atacado 
        vals['description'] = 'atualizado'      
     
    # Para teste em um Produto     
    #if prd_a.barcode == '7898929293916':
    #    #import pudb;pu.db
    #    if len(vals):
    #        b_prod.write([prd_b.id], vals)
   
    # Para Atualizar pelo offset= ? ,limit= ?
    if len(vals):
        b_prod.write([prd_b.id], vals)        
        cadastra += 1
        print ('Codigo : %s , Produto : %s , CodBarra : %s , Valor : %s '  % (prd_a.id, prd_a.name,prd_a.barcode, prd_a.lst_price))
    #import pudb;pu.db
    #if prd.barcode == '7898929293916':
    #    print ('Codigo : %s , Produto : %s , CodBarra : %s , Valor : %s '  % (prd.id, prd.name,prd.barcode, prd.lst_price))

'''
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
        #prod_odoo['fiscal_category_id'] =  1 
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
        
        #print ('Categoria :%s , Produto : %s.' % (prd.categ_id.name, prd.name))
        print ('Codigo : %s ,Categoria :%s , Produto : %s.' % (prd.categ_id.id,prd.categ_id.name, prd.name))
        # Descomentar se quiser inserir o produto
        #id_prod = b_prod.create(prod_odoo)
'''
if cadastra > 0:
    #print ('Corrigido %s produtos , nome %s ,codbarra %s ' % (str(cadastra),prd_b.name, prd_b.barcode))
    print ('Corrigido %s produtos' % (str(cadastra)))
else:
    print ('Nenhum cadastro PRODUTO a ser Corrigido.')


