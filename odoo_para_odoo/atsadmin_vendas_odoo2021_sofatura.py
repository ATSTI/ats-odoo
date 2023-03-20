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

#CONEXAO ODOO
# Prepare the connection to the server
#odoo = odoorpc.ODOO('192.168.6.100', port=8069)
odoo = odoorpc.ODOO('127.0.0.1', port=9090)
# Login
#odoo.login('19_conquista', 'ats@atsti.com.br', 'a2t00s7')
odoo.login('fritisco', 'ats@atsti.com.br', 'a2t00s7')


odoo_user = odoo.env['res.users']


# VENDAS
odoo_inv = odoo.env['account.invoice']
odoo_move = odoo.env['account.move']
odoo_vnd = odoo.env['sale.order']
odoo_prd = odoo.env['product.product']
odoo_parc = odoo.env['res.partner']
odoo_cfop = odoo.env['br_account.cfop']
odoo_user = odoo.env['res.users']
dt_ord = '01.10.2020'
dt_ordb = '31.10.2020'

print ('---------------------------------------')
print (' COMECANDO SCRIPT DE :  %s' %(dt_ord))
print ('--------------------------------------')

sqlv = 'SELECT m.CODMOVIMENTO, m.DATAMOVIMENTO, \
       m.CODCLIENTE, m.STATUS, m.CODUSUARIO, m.CODVENDEDOR, \
       m.CODALMOXARIFADO, DATEADD(3 hour to m.DATA_SISTEMA) \
       ,v.N_PARCELA, v.DATAVENCIMENTO, v.NOTAFISCAL, v.SERIE \
       , v.VALOR \
       FROM MOVIMENTO m , VENDA v \
       WHERE v.CODMOVIMENTO = m.CODMOVIMENTO \
         AND m.CODNATUREZA = 3 \
         AND m.datamovimento between \'%s\' and \'%s\' order by m.codmovimento' %(dt_ord, dt_ordb)
cur.execute(sqlv)

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
        cli_id = odoo_parc.search([('ref', '=', str(cli)),
            ('customer','=', True),
            ('active', '=', False)])
        if not cli_id:
            print ('CLIENTE NAO ENCONTRADO CCCCCCCCCCCCCC %s, %s, %s' %(str(cli),nf, ord_name))
            continue
    cli = cli_id[0]
    vendedor = odoo_user.search([('name', '=', mvs[5])])
    dt_orde = str(mvs[1]) + ' 12:00:00'
    #dt_ord = str(mvs[7])
    sale_ids = odoo_vnd.search([('client_order_ref', '=', ord_name)])
    data_in = mvs[1]
    # import pudb;pu.db
    if not sale_ids:
        msg_sis = 'INSERINDO ---------- : %s - %s <br>' %(str(mvs[0]), data_in )
        print(msg_sis)
        vals['name'] = nf
        vals['origin'] = 'ATS-Admin-%s' %(str(mvs[0]))
        vals['client_order_ref'] = ord_name
        vals['create_date'] = dt_orde #datetime.strftime(datetime.now(),'%Y-%m-%d %H:%M:%S')
        vals['date_order'] = dt_orde
        vals['partner_id'] = cli
        vals['partner_invoice_id'] = cli
        vals['partner_shipping_id'] = cli
        vals['user_id'] = vendedor
        userid = mvs[5]
        vals['fiscal_position_id'] = 1
        vals['payment_term_id'] = 1

        #ord_id = odoo_vnd.create(vals)
        """"""
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
        # print(msg_sis)
        sale = odoo_vnd.browse(sale_ids)
        #    'partner_id': cli, 
        if sale.state == 'draft':
            odoo_vnd.write(sale_ids, {        
                'date_order': dt_orde,
                'user_id': vendedor,
            })
            #odoo_vnd.write(sale_ids, {'user_id': vendedor})
            sale.action_confirm()
        if sale.state == 'sale':
            inv_ids = odoo_inv.search([('origin', '=', nf)])
            invoice = odoo_inv.browse(inv_ids)
            diferenca_vlr = mvs[12] - invoice.amount_total
            if diferenca_vlr < 0.0:
                diferenca_vlr = diferenca_vlr * (-1)
            sqlr = 'SELECT First 1  r.titulo, r.datavencimento, \
                r.datarecebimento, r.status, r.via, r.parcelas, \
                r.valortitulo, r.valor_resto, r.CAIXA \
                from recebimento r , venda v \
                where v.codvenda = r.codvenda \
                  and v.codmovimento = %s ' %(str(mvs[0]))
            cur.execute(sqlr)
            # import pudb;pu.db
            situacao = '7-'
            for rec in cur.fetchall():
                if rec[3] != situacao:
                    situacao = rec[3]
            if diferenca_vlr < 0.01 and situacao == '7-':
                print (' continuado nada a fazer aqui - %s ' %(nf))
                continue
            if diferenca_vlr < 0.01 and invoice.state == 'open':
                print (' continuado nada a fazer aqui - %s ' %(nf))
                continue
            if not inv_ids:                
                # inv_ids = sale.action_invoice_create()
                print (' @@@@@@@@@@@ nao achou a fatura - %s ' %(nf))
                continue
            else:
                if invoice.amount_total < mvs[12] or situacao == '5-':
                    if invoice.state == 'paid' and situacao == '5-':
                        invoice.action_invoice_cancel_paid()
                        invoice.action_invoice_draft()
                move_ids = odoo_move.search([('ref','=',nf)])
                move = odoo_move.browse(move_ids)
                for mv in move:
                    mv.reverse_moves()
                    for linha_move in mv.line_ids:
                        linha_move.write({'name': linha_move.name + 'EXCLUIR'})
                #move = odoo_move.browse(move_ids)
                #move.unlink()
            inv = odoo_inv.browse(invoice.id)
            # insiro ST na fatura            
            if inv.amount_total < mvs[12]:
                diferenca = mvs[12] - inv.amount_total
                # faco o rateio pelos itens
                total_rateio = 0.0
                num_linha = len(inv.invoice_line_ids)
                conta_linha = 0
                for linha_fatura in inv.invoice_line_ids:
                    conta_linha += 1
                    if conta_linha < num_linha and inv.amount_total:
                        rateio = (linha_fatura.price_subtotal / inv.amount_total) * diferenca
                        total_rateio += rateio
                    else:
                        rateio = diferenca - total_rateio
                    linha_fatura.write({'outras_despesas': rateio})
            if inv.state in ('paid', 'cancel'):
                continue
            sqlr = 'SELECT First 1 r.titulo, r.datavencimento, \
                r.datarecebimento, r.status, r.via, r.parcelas, \
                r.valortitulo, r.valor_resto, r.CAIXA \
                from recebimento r , venda v \
                where v.codvenda = r.codvenda \
                  and v.codmovimento = %s ' %(str(mvs[0]))
            cur.execute(sqlr)
            #import pudb;pu.db
            for rec in cur.fetchall():
                if inv.state == 'draft':
                    msg_sis = 'INSERINDO FATURA ---------- %s<br>' %(ord_name)
                    #import pudb;pu.db
                    inv.date_invoice = dt_orde[:10]
                    inv.name = ord_name
                    inv.reference = nf
                    inv.number = nf
                    inv.payment_term_id = False
                    inv.num_parcela = n_parcela
                    
                    dat = rec[1]
                    inv.dia_vcto = dat.day
                    dat = datetime.strftime(rec[1],'%Y-%m-%d')
                    inv.date_due = dat
                    
                    inv.action_calcula_parcela()
                    
                    inv.action_invoice_open()
                    #inv = odoo_inv.browse(inv.id)
                # pegar o BANCO/CAIXA
                if rec[3] == '5-':
                    continue
                #import pudb;pu.db


     
print ('Feito importacao vendas : %s' %(dt_ord))

print ('------------------------------')
print ('Importando Faturas')
print ('------------------------------')


sqlr = 'SELECT r.codrecebimento, r.titulo, r.datavencimento, \
            r.datarecebimento, r.status, r.via, r.parcelas, \
            r.valortitulo, r.valor_resto, r.CAIXA, \
            r.emissao, r.codcliente , r.codusuario, u.NOMEUSUARIO \
            from recebimento r left outer join USUARIO u on u.codusuario = r.codusuario  \
            WHERE  r.codvenda IS NULL  \
            AND r.emissao between \'%s\' and \'%s\' order by r.codrecebimento' %(dt_ord, dt_ordb)
        #    and r.codrecebimento = 0            \
cur.execute(sqlr)
for mvs in cur.fetchall():
    data_emissao = datetime.strftime(mvs[10],'%Y-%m-%d')
    msg_sis = 'Fatura_cheque : %s<br>' %(str(mvs[0]))
    cod_rec = '%s' %(str(mvs[0]))
    titulo = '%s' %(str(mvs[1]))
    n_parcela = mvs[8]
    vencimento = datetime.strftime(mvs[2],'%Y-%m-%d')
    msg_sis = 'Importando : %s - %s <br>' %(str(mvs[0]), data_emissao )
    vals = {}               
    cli = mvs[11]
    cli_id = odoo_parc.search([('ref', '=', str(cli)),('customer','=', True)])
    if not cli_id:
        cli_id = odoo_parc.search([('ref', '=', str(cli)),
            ('customer','=', True),
            ('active', '=', False)])
        if not cli_id:
            print ('CLIENTE NAO ENCONTRADO CCCCCCCCCCCCCC %s, %s, %s' %(str(cli),nf, ord_name))
            continue
    cli = cli_id[0]
    vendedor = odoo_user.search([('name', '=', mvs[13])])
    dt_orde = data_emissao + ' 12:00:00'
    #dt_ord = str(mvs[7])
    inv_ids = odoo_inv.search([('origin', '=', str(cod_rec))])
    data_in = mvs[1]
    # import pudb;pu.db
    if not inv_ids:
        msg_sis = 'INSERINDO FATURAS CHEQUES---------- : %s - %s <br>' %(str(mvs[0]), data_emissao )
        print(msg_sis)
        vals['name'] = titulo
        vals['origin'] = str(cod_rec)
        vals['reference'] = titulo
        vals['create_date'] = dt_orde #datetime.strftime(datetime.now(),'%Y-%m-%d %H:%M:%S')
        vals['date_invoice'] = data_emissao
        vals['date_due'] = vencimento
        vals['partner_id'] = cli
        if vendedor:
            vals['user_id'] = vendedor[0]
        vals['fiscal_position_id'] = 1
        vals['payment_term_id'] = 1

        # prod_ids = odoo_prd.search([('default_code', '=', str(md[1]))])
        prod = 557
        prd = {}
        order_line = []
        prd_id = odoo_prd.browse(prod)
        prd['product_id'] = prod
        prd['price_unit'] = mvs[7]
        prd['quantity'] = 1
        prd['account_id'] = 20
        prd['name'] = prd_id.name
        order_line.append((0, 0,prd))

        vals['invoice_line_ids'] = order_line
        try:
            #import pudb;pu.db
            invoice = odoo_inv.create(vals)
            inv = odoo_inv.browse(invoice)
            inv.action_invoice_open()
        except:
            print ('Erro XXXXX pedido %s' %(ord_name))
            continue
    # else:
    #     invoice = odoo_inv.browse(inv_ids)
    #     invoice.action_invoice_cancel()
    #     # invoice.action_invoice_draft()        
    continue    

print ('Feito importacao faturas : %s' %(dt_ord))

print ('------------------------------')
print ('Corrigindo pendente errado')
print ('------------------------------')

# import pudb;pu.db
sqlr = 'SELECT r.titulo, r.datavencimento, r.datarecebimento, \
            r.status, r.via, r.parcelas, r.valortitulo, \
            r.valor_resto, r.CAIXA, r.codrecebimento, r.valorrecebido, \
            r.codcliente \
            from recebimento r \
            where r.status = \'5-\' \
            AND r.emissao between \'%s\' and \'%s\' order by r.codrecebimento' %(dt_ord, dt_ordb)

cur.execute(sqlr)

for rec in cur.fetchall():
    cod_rec = str(rec[9])
    titulo = rec[0]
    #if titulo == '110997-S':
    #    import pudb;pu.db
    # if cod_rec == '41397':        
    inv = odoo_inv.search(['|',('origin', '=', cod_rec),
        ('reference', '=', titulo),
    ],limit=1)
    invoice = odoo_inv.browse(inv)
    if invoice and invoice.residual == rec[7]:
        continue
    if invoice.state == 'open':
        continue
    #if invoice.state not in 'open':
    #    continue
    print (' VOLTANDO A FATURA PARA ABERTO - %s' %(titulo))
    invoice.action_invoice_cancel_paid()
    invoice.action_invoice_draft()
    move_ids = odoo_move.search([('ref','=',titulo)])
    move = odoo_move.browse(move_ids)
    for mv in move:
        mv.reverse_moves()
        for linha_move in mv.line_ids:
            linha_move.write({'name': linha_move.name + 'EXCLUIR'})
    invoice.action_calcula_parcela()
    try:
        invoice.action_invoice_open()
    except:
        print (' #######  Falha para confirmar Fatura - %s' %(titulo))



print ('------------------------------')
print ('Baixando Faturas')
print ('------------------------------')

# import pudb;pu.db
sqlr = 'SELECT r.titulo, r.datavencimento, r.datarecebimento, \
            r.status, r.via, r.parcelas, r.valortitulo, \
            r.valor_resto, r.CAIXA, r.codrecebimento, r.valorrecebido, \
            r.codcliente \
            from recebimento r \
            where r.status = \'7-\' \
            AND r.emissao between \'%s\' and \'%s\' order by r.codrecebimento' %(dt_ord, dt_ordb)

cur.execute(sqlr)

for rec in cur.fetchall():
    cod_rec = str(rec[9])
    titulo = rec[0]
    # if titulo == '000050':
        # import pudb;pu.db
    # if cod_rec == '41397':        
    invoice = odoo_inv.search(['|',('origin', '=', cod_rec),
        ('reference', '=', titulo),
        ('state', '=', 'open'),
    ])
    if not invoice:
        continue
    inv = odoo_inv.browse(invoice)
    if inv.state not in 'open':
        continue
    # vejo se ja baixou
    cli = rec[11]
    cli_id = odoo_parc.search([('ref', '=', str(cli)),('customer','=', True)])
    if not cli_id:
        cli_id = odoo_parc.search([('ref', '=', str(cli)),
            ('customer','=', True),
            ('active', '=', False)])
        if not cli_id:
            print ('CLIENTE NAO ENCONTRADO @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ %s, %s, %s' %(str(cli),nf, ord_name))
            continue
    cli = cli_id[0]
    dat = datetime.strftime(rec[1],'%Y-%m-%d')
    if rec[2]:
        dat = datetime.strftime(rec[2],'%Y-%m-%d')    
    m_line = odoo.env['account.move.line'].search([
        ('partner_id', '=', cli),
        ('date', '=', dat),
        ('name', 'like', 'Pagamento'),
        ('ref','=',titulo)
    ])
    if m_line:
        # import pudb;pu.db
        move_linha = odoo.env['account.move.line'].browse(m_line)
        linha_excluir = 'N'
        for mvl in move_linha:
            linha_excluir = 'N'
            if 'EXCLUIR' in mvl.name:
                linha_excluir = 'S'
            #if mvl.partner_id.id == 641:
            #    import pudb;pu.db
        if linha_excluir == 'N':
            continue

    diario = 11
    msg_sis = 'BAIXANDO FATURA ---------- : %s <br>' %(titulo)
    print(msg_sis)
    if rec[8] == 33:
        diario = 11
    if rec[8] == 103:
        diario = 9
    if rec[8] == 104:
        diario = 10
    if rec[8] == 175:
        diario = 8
                
    #inv.action_invoice_paid()
    arp = odoo.env['account.register.payments']    
    pag = arp.with_context(active_model='account.invoice')
    ctx = {'active_model': 'account.invoice', 'active_ids': [inv.id]}
    register_payments = pag.with_context(ctx).create({
        'payment_date': dat,
        'journal_id': diario,
        'amount': rec[10],
        'payment_method_id': odoo.env.ref('account.account_payment_method_manual_in').id,
    })
    #import pudb;pu.db
    rg = arp.browse(register_payments)
    rg.create_payments()


print ('---------------------------------------')
print (' ENCERRADO SCRIPT ATE :  %s' %(dt_ordb))
print ('--------------------------------------')
