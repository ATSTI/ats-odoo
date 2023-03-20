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
prd_ids = a_prod.search([('write_date', '>', '2022-10-01')], offset=0,limit=500, order = "default_code" )


#prd_ids = a_prod.search([], limit=10,order=prd)
cadastra = 0
for prd_a in a_prod.browse(prd_ids):
    # aqui vai procurar pelo Codigo  OU pelo codigo de barra
    prod_id = b_prod.search(['|',('default_code', '=', prd_a.default_code), ('barcode', '=', prd_a.barcode)])    
    
    #if not prd_a.barcode:
    #   continue
    
    prd_b = b_prod.browse(prod_id)
    vals = {}
    
    
    if prd_b.name != prd_a.name:
        vals['name'] = prd_a.name
    if prd_b.lst_price != prd_a.lst_price:
        vals['lst_price'] = prd_a.lst_price
        vals['standard_price'] = prd_a.standard_price
    if prd_b.margin != prd_a.margin:
        vals['margin'] = prd_a.margin
    if prd_b.qtde_atacado != prd_a.qtde_atacado:
        vals['qtde_atacado'] = prd_a.qtde_atacado
    if prd_b.preco_atacado != prd_a.preco_atacado:
        vals['preco_atacado'] = prd_a.preco_atacado    
     
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


if cadastra > 0:
    #print ('Corrigido %s produtos , nome %s ,codbarra %s ' % (str(cadastra),prd_b.name, prd_b.barcode))
    print ('Corrigido %s produtos' % (str(cadastra)))
else:
    print ('Nenhum cadastro PRODUTO a ser Corrigido.')


