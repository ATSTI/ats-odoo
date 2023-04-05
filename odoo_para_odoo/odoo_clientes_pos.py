# -*- coding: utf-8 -*-

import odoorpc
# import fiscal
import re
from datetime import datetime
from datetime import date
from datetime import timedelta
from unidecode import unidecode
from erpbrasil.base.fiscal import cnpj_cpf
import json
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
a_user = dest.env['res.users']

a_session = origem.env['pos.session']
b_session = dest.env['pos.session']

a_pedido = origem.env['pos.order']
b_pedido = dest.env['pos.order']

b_pedidoLine = dest.env['pos.order.line']
b_pedidoPag = dest.env['pos.payment']

#odoo_city = odoo.env['res.state.city']
#odoo_fiscal = odoo.env['br_base.tools.fiscal']

hj = datetime.now()
hj = hj - timedelta(days=5)
hj = datetime.strftime(hj,'%Y-%m-%d %H:%M:%S')

######## IMPORTAR Clientes
cadastra = 0

#a_todos_cli = a_cliente.search([], limit=50)
#a_todos_cli = a_cliente.search([('id', '>',3000), ('id', '<', 3500)], order = "id")

#a_todos_cli = a_cliente.search([('name', '=', cli.name)])

def baixa_pagamentos(move_line_id, journal_id, caixa, valor, cod_forma, juros):
    if journal_id:
        invoices = move_line_id
        # amount = self._compute_payment_amount(invoices=invoices) if self.multi else self.amount
        if move_line_id.amount_residual > valor or ((move_line_id.amount_residual - valor) > 0.01):
            baixar_tudo = 'open'
        else:
            baixar_tudo = 'reconcile'
        bank_account = invoices.partner_bank_id or invoices.partner_bank_account_id
        # pmt_communication = self._prepare_communication(invoices)

        payment_type = 'inbound'# if move_line_id.debit else 'outbound'
        payment_methods = \
            payment_type == 'inbound' and \
            journal_id.inbound_payment_method_ids or \
            journal_id.outbound_payment_method_ids
        payment_method_id = payment_methods and payment_methods[0] or False
        vals = {
            'journal_id': journal_id.id,
            'payment_method_id': payment_method_id.id,
            'payment_date': datetime.now(),
            'communication': invoices.name,
            'invoice_ids': [(6, 0, invoices.ids)],
            'payment_type': payment_type,
            'amount': valor,
            'currency_id': journal_id.company_id.currency_id.id,
            'partner_id': move_line_id.partner_id.id,
            'partner_type': 'customer',
            'partner_bank_account_id': bank_account.id,
            'multi': False,
            'payment_difference_handling': baixar_tudo,
            'writeoff_label': 'importados'
        }
        Payment = dest.env['account.payment']        
        pay = Payment.create(vals)
        pay.post()
ses_num = 466
a_ses = a_session.search([('id', '>',ses_num-1), ('id', '<',ses_num+1)], order = "id") #feito hj 29 ate o 463
def insere_pedido(sNova,sVelha):
    pedidos = a_pedido.search([('session_id', '=', sVelha)])
    
    for ped in a_pedido.browse(pedidos):
        pedb = b_pedido.search([('name', '=', ped.name )])
        #import pudb;pu.db
        
        if pedb:
            continue
        
        vals = {}
        vals['name'] = ped.name
        vals['session_id'] = sNova
        vals['date_order'] = datetime.strftime(ped.date_order,'%Y-%m-%d')

        part = dest.env['res.partner'].search([('name', '=', ped.partner_id.name)])
        if len(part):
            vals['partner_id'] = part[0]

        vals['amount_tax'] = ped.amount_total
        vals['amount_total'] = ped.amount_total
        vals['amount_paid'] = ped.amount_paid
        vals['amount_return'] = ped.amount_return
        vals['company_id'] = 1
        vals['pricelist_id'] = 1
        #import pudb;pu.db
        ped_id = b_pedido.create(vals) 
        list_adi = []
        for line in ped.lines:
            prod = dest.env['product.product'].search([('default_code', 'ilike', line.product_id.default_code)])
            if not prod:
                prod = dest.env['product.product'].search([('name', '=', line.product_id.name)]) 
            vals_iten = {
                #"id" : line.id,
                "name": line.name,
                "product_id": prod[0], 
                "full_product_name" :line.product_id.name,
                "discount": line.discount,
                "qty": line.qty,
                "price_unit": line.price_unit,
                "tipo_venda": line.tipo_venda,
                "price_subtotal": line.price_subtotal,
                "price_subtotal_incl": line.price_subtotal_incl,
                "order_id": ped_id,
                
            }
            #import pudb;pu.db
            vLine = b_pedidoLine.create(vals_iten)            
           
            #list_adi.append(vLine[0])
            
        #vals['lines'] = [(6, 0, list_adi)]          
        
        #  aqui aba pagamento 
        list_pag = []
        for pag in ped.statement_ids :
            metodo_pag = dest.env['pos.payment.method'].search([('name', 'ilike', pag.journal_id.name[:2])])       
            vals_pag = {
                "name": pag.name,                
                "pos_order_id": ped_id,
                "amount": pag.amount,                     
                "payment_method_id": metodo_pag[0],     
                "payment_date": datetime.strftime(pag.date,'%Y-%m-%d'),
                "session_id": sNova ,
            }
            #import pudb;pu.db
            vLine = b_pedidoPag.create(vals_pag)
  
        # mudando o status pra pago
        pd = b_pedido.browse([ped_id])
        pd.action_pos_order_paid()
        
        # se a prazo criando a Fatura
        if metodo_pag == '4-':
            import pudb;pu.db
            pd.write({'to_invoice': True})
            move_vals = pd._prepare_invoice_vals()
            new_move = pd._create_invoice(move_vals)
            pd.write({'account_move': new_move.id, 'state': 'invoiced'})
            new_move.sudo().with_company(pd.company_id)._post()
         
            # ver se esta paga

            # if ped.invoice_id.state == 'paid':
            for ct in ped.invoice_id.receivable_move_line_ids:
                if ct.reconciled:
                    bancos = origem.env['account.journal'].search([
                        ('type', 'in', ('cash', 'bank'))])
                    aml = origem.env['account.move.line'].search([
                        ('ref','=',ped.name),
                        ('journal_id', 'in', bancos)
                    ])
                    for ml in aml:
                        aml_id = origem.env['account.move.line'].browse(ml)
                        jrn = dest.env['account.journal'].search([('name', 'ilike', ml.journal_id.name[:2])])
                        jrn_id = dest.env['account.journal'].browse(jrn)
                        baixa_pagamentos(new_move, jrn_id, 0, aml_id.debit, 0, 0)

        """
        # aba informacao adicionais
        list_inf = []
        for inf in ped.pos.order :
            vals_inf = {
                "session_move_id": inf.picking_id ,                
                "pos_reference": inf.pos_reference,    
            }
            #import pudb;pu.db
            vLine = b_pedidoPag.create(vals_inf)            
           
        #    list_inf.append(vLine[0])
            
        #vals['account_move'] = [(6, 0, list_inf)] 

        #b_pedidoPag.create(vals_inf)             
        """   
        
for ses in a_session.browse(a_ses): 
    #import pudb;pu.db
    #cli_id = b_cliente.search([('name', '=', cli.name)])
    #print ('Codigo : %s , Nome : %s.' % (cli.id,cli.name))
    #print ('Codigo odoo 14 : %s ' % (cli_id)) 
    
    pSession = b_session.search([('name', 'ilike', ses.name )])
    if pSession:
        insere_pedido(pSession[0],ses.id)
        continue     
    vals = {}
    
    user = a_user.search([('name', '=', ses.user_id.name)])

    #if ses.stop_at:
    vals['user_id'] = user[0]
    vals['name'] = ses.name
    vals['config_id'] = ses.config_id.id
    vals['start_at'] = datetime.strftime(ses.start_at,'%Y-%m-%d')
    vals['stop_at'] = datetime.strftime(ses.stop_at,'%Y-%m-%d')
    vals['state'] = 'closed'    
    
    '''
    if ses.stop_at == False:
        vals['user_id'] = user[0]
        vals['name'] = ses.name
        vals['config_id'] = ses.config_id.id
        vals['start_at'] = datetime.strftime(ses.start_at,'%Y-%m-%d')
        vals['state'] = 'opened'
    '''

    pSession_id = b_session.create(vals)
    insere_pedido(pSession_id,ses.id)   
  

