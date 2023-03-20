# -*- coding: utf-8 -*-

import fdb
import odoorpc
import fiscal
import re
from datetime import datetime
from datetime import date
from datetime import timedelta
from unidecode import unidecode
import sys
#reload(sys)
#sys.setdefaultencoding("utf-8")

# CONEXAO ATS-ADMIN
#con = fdb.connect(dsn='192.168.0.111:/home/bd/sge_fritisco.fdb', user='sysdba', password='masterkey',charset='UTF8')
con = fdb.connect(dsn='192.168.6.20:/home/bd/sge_fritisco.fdb', user='sysdba', password='masterkey',charset='UTF8')
#con = fdb.connect(dsn='192.168.6.251/3050:/home/sisadmin/bd/sge_felicita.fdb', user='sysdba', password='masterkey',charset='UTF8')
# Abre conexao com o banco da Sao Pedro Treino:
cur = con.cursor()
import pudb;pu.db
#CONEXAO ODOO
# Prepare the connection to the server
odoo = odoorpc.ODOO('192.168.6.100', port=8069)
#odoo = odoorpc.ODOO('127.0.0.1', port=9090)
# Login
#odoo.login('19_conquista', 'ats@atsti.com.br', 'a2t00s7')
odoo.login('fritisco', 'ats@atsti.com.br', 'a2t00s7')


odoo_user = odoo.env['res.users']


# VENDAS
odoo_inv = odoo.env['account.invoice']
odoo_vnd = odoo.env['sale.order']
odoo_prd = odoo.env['product.product']
odoo_parc = odoo.env['res.partner']
odoo_cfop = odoo.env['br_account.cfop']
odoo_user = odoo.env['res.users']
dt_ord = '01.12.2021'
dt_ordb = '31.12.2021'
sqlv = 'SELECT m.CODMOVIMENTO, m.DATAMOVIMENTO, \
       m.CODCLIENTE, m.STATUS, m.CODUSUARIO, m.CODVENDEDOR, \
       m.CODALMOXARIFADO, DATEADD(3 hour to m.DATA_SISTEMA) \
       ,v.N_PARCELA, v.DATAVENCIMENTO, v.NOTAFISCAL, v.SERIE \
       FROM MOVIMENTO m , VENDA v \
       WHERE v.CODMOVIMENTO = m.CODMOVIMENTO \
         AND m.CODNATUREZA = 3 \
         AND m.CODCLIENTE = 772 \
         AND v.NOTAFISCAL = 129598 \
         AND m.datamovimento between \'%s\' and \'%s\' order by m.codmovimento' %(dt_ord, dt_ordb)
cur.execute(sqlv)
#simport pudb;pu.db
for mvs in cur.fetchall():
    data_mov = mvs[1]
    msg_sis = 'Pedidos : %s<br>' %(str(mvs[0]))
    ord_name = '%s' %(str(mvs[0]))
    nf = '%s-%s' %(str(mvs[10]), str(mvs[11]))
    n_parcela = mvs[8]
    vencimento = mvs[9]
    msg_sis = 'Importando : %s - %s <br>' %(str(mvs[0]), data_mov )
    vals = {}               
    cli = mvs[2]
    cli_id = odoo_parc.search([('ref', '=', str(cli)),('customer','=', True)])
    if not cli_id:
        print ('CLIENTE NAO ENCONTRADO CCCCCCCCCCCCCC %s, %s, %s' %(str(cli),nf, ord_name))
        continue
    cli = cli_id[0]
    vendedor = odoo_user.search([('name', '=', mvs[5])])
    #vendedor = mvs[5]
    #if vendedor not in (1,4,2,23):
    #    print ('VENDEDOR NAO ENCONTRADO TTTTTTTTTTTTT %s, %s, %s' %(str(vendedor), nf, ord_name))
    #    continue
    #if vendedor == 1:
    #    vendedor = 19
    #if vendedor == 4:
    #    vendedor = 21
    #if vendedor == 2:
    #    vendedor = 20
    #if vendedor == 23:
    #    vendedor = 6
    #dt_ord = str(mvs[1]) + ' 12:00:00'
    dt_ord = str(mvs[7])
    sale_ids = odoo_vnd.search([('client_order_ref', '=', ord_name)])
    data_in = mvs[1]
    if not sale_ids:
        msg_sis = 'INSERINDO ---------- : %s - %s <br>' %(str(mvs[0]), data_in )
        print(msg_sis)
        vals['name'] = nf
        vals['origin'] = 'ATS-Admin-%s' %(str(mvs[0]))
        vals['client_order_ref'] = ord_name
        vals['create_date'] = dt_ord #datetime.strftime(datetime.now(),'%Y-%m-%d %H:%M:%S')
        vals['date_order'] = dt_ord
        vals['partner_id'] = cli
        vals['partner_invoice_id'] = cli
        vals['partner_shipping_id'] = cli
        vals['user_id'] = vendedor
        userid = mvs[5]
        vals['fiscal_position_id'] = 1
        vals['payment_term_id'] = 1

        #ord_id = odoo_vnd.create(vals)
        order_line = []
        sqld = 'SELECT md.CODDETALHE, pro.CODPRO, \
               md.QUANTIDADE, md.PRECO, COALESCE(md.VALOR_DESCONTO,0), \
               md.BAIXA, md.DESCPRODUTO, COALESCE(md.CFOP,\'5102\') \
                FROM MOVIMENTODETALHE md, PRODUTOS pro  \
                WHERE pro.CODPRODUTO = md.CODPRODUTO and md.CodMovimento = %s' %(str(mvs[0]))
        cur.execute(sqld)
        #order = pos_ord.browse(ord_id)
        #order.write({'fiscal_position_id' : })
        vlr_total = 0.0
        vlr_totprod = 0.0
        for md in cur.fetchall():
            vlr_total += (md[2]*md[3])-md[4]
            vlr_totprod = (md[2]*md[3])-md[4]
            desconto = 0.0
            #   teve_desconto = 's'
            #      desconto = md[4] / (vlr_totprod+md[4])
            prd = {}
            cfop = 297
            if md[7].strip():
                cfop = md[7].strip()
                if cfop != '5102':
                    cfop = odoo_cfop.search([('code', '=', cfop)])
                    if not cfop:
                        cfop = odoo_cfop.search([('code', '=', '5102')])
                    cfop = cfop[0]
                else:
                    cfop = 297

            prod_ids = odoo_prd.search([('default_code', '=', str(md[1]))])
            if not prod_ids:
                prod_ids = odoo_prd.search([
                   ('active','=',False),
                   ('default_code', '=', str(md[1]))])
            if not prod_ids:
                print ('SEM PRODUTO NO CADASTRO @@@@@@@@#### PEDIDO %s - %s' %(ord_name, str(md[1])))
                continue
            prd_id = odoo_prd.browse(prod_ids)
            try:
                prdname = unidecode(md[6])
            except:
                prdname = prd_id.name
            
            if prd_id:
                prd['product_id'] = prd_id.id
            else:
                print ('Erro item %s, pedido %s' %(str(md[1]), ord_name))
            #prd['discount'] = desconto
            prd['product_uom_qty'] = md[2]
            prd['product_uom'] = prd_id.uom_id.id
            prd['price_unit'] = md[3]
            prd['name'] = prdname
            prd['cfop_id'] = cfop
            prd['icms_cst_normal'] = '40'
            prd['ipi_cst'] = '99'
            prd['pis_cst'] = '06'
            prd['cofins_cst'] = '06'
            order_line.append((0, 0,prd))

            #vals['amount_return'] = vlr_total
        vals['order_line'] = order_line
        try:
            #import pudb;pu.db
            venda_n = odoo_vnd.create(vals)
        except:
            print ('Erro XXXXX pedido %s' %(ord_name))
            continue
    else:
        #import pudb;pu.db
        print(msg_sis)
        sale = odoo_vnd.browse(sale_ids)
        #    'partner_id': cli, 
        if sale.state == 'draft':
            odoo_vnd.write(sale_ids, {        
                'date_order': dt_ord,
                'user_id': vendedor,
            })
            #odoo_vnd.write(sale_ids, {'user_id': vendedor})
            sale.action_confirm()
        if sale.state == 'sale':
            inv_ids = odoo_inv.search([('origin', '=', nf)])
            if not inv_ids:                
                inv_ids = sale.action_invoice_create()
            inv = odoo_inv.browse(inv_ids)
            if inv.state == 'draft':
                msg_sis = 'INSERINDO VENDA ---------- %s<br>' %(ord_name)
                #import pudb;pu.db
                inv.date_invoice = dt_ord[:10]
                inv.name = ord_name
                inv.reference = nf
                inv.number = nf
                inv.payment_term_id = False
                inv.num_parcela = n_parcela
                inv.dia_vcto = vencimento.day
                inv.action_calcula_parcela()
                # deve estar dando algum erro aqui na linha debaixo
                #import pudb;pu.db
                inv.action_invoice_open()
            if inv.state in ('draft', 'paid', 'cancel'):
                continue
            sqlr = 'SELECT r.titulo, r.datavencimento, \
                r.datarecebimento, r.status, r.via, r.parcelas, \
                r.valortitulo, r.valor_resto, r.CAIXA \
                from recebimento r , venda v \
                where v.codvenda = r.codvenda \
                  and v.codmovimento = %s ' %(str(mvs[0]))
            cur.execute(sqlr)
            #import pudb;pu.db
            for rec in cur.fetchall():
                # pegar o BANCO/CAIXA
                diario = 11
                if rec[8] == 33:
                    diario = 11
                if rec[8] == 103:
                    diario = 9
                if rec[8] == 104:
                    diario = 10
                if rec[8] == 175:
                    diario = 8
                
                #inv.action_invoice_paid()
                dat = datetime.strftime(rec[1],'%Y-%m-%d')
                if rec[2]:
                    dat = datetime.strftime(rec[2],'%Y-%m-%d')
                arp = odoo.env['account.register.payments']    
                pag = arp.with_context(active_model='account.invoice')
                ctx = {'active_model': 'account.invoice', 'active_ids': [inv.id]}
                register_payments = pag.with_context(ctx).create({
                    'payment_date': dat,
                    'journal_id': diario,
                    'payment_method_id': odoo.env.ref('account.account_payment_method_manual_in').id,
                })
                #import pudb;pu.db
                rg = arp.browse(register_payments)
                rg.create_payments()
                
        
        continue
    
        #venda_n.action_confirm()
        #inv_ids = sale.action_invoice_create()
        #inv = odoo_inv.browse(inv_ids)
        #inv.date_invoice = dt_ord
        #inv.name = nf
        #inv.reference = nf
        #inv.number = nf

        #inv.payment_term_id = False
        #inv.num_parcela = n_parcela
        #inv.dia_vcto = vencimento.day
        #inv.action_calcula_parcela()
        #inv.action_invoice_open()
     
        sqlr = 'SELECT r.titulo, r.datavencimento, \
           r.datarecebimento, r.status, r.via, r.parcelas, \
           r.valortitulo, r.valor_resto, r.CAIXA, r.VALORRECEBIDO \
           from recebimento r , venda v \
            where v.codvenda = r.codvenda \
              and r.STATUS = \'7-\' \
              and v.codmovimento = %s ' %(str(mvs[0]))
        cur.execute(sqlr)
        for rec in cur.fetchall():
            # pegar o BANCO/CAIXA
            if rec[8] == 33:
                diario = 11
            if rec[8] == 103:
                diario = 9
            if rec[8] == 104:
                diario = 10
            if rec[8] == 175:
                diario = 8
               
               
            arp = odoo.env['account.register.payments']
            pag = arp.with_context(active_model='account.invoice')
            ctx = {'active_model': 'account.invoice', 'active_ids': [inv.id]}
            register_payments = pag.with_context(ctx).create({
                'payment_date': datetime.strftime(rec[2],'%Y-%m-%d'),
                'journal_id': diario,
                'payment_method_id': odoo.env.ref('account.account_payment_method_manual_in').id,
            })
            rg = arp.browse(register_payments)
            rg.create_payments()
     
print ('Feito importacao vendas : %s' %(dt_ord))
