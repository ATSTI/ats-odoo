# -*- coding:utf-8 -*-

from odoo import models, fields, api, tools, _
# from odoo.addons.point_of_sale.wizard.pos_box import PosBox
# from odoo.exceptions import UserError
from datetime import datetime, date, timedelta
# from unidecode import unidecode
import logging
# import psycopg2
import os
import json

# from . import atscon as con


_logger = logging.getLogger(__name__)

class PosSession(models.Model):
    _inherit = 'pos.session'
    
    def baixa_pagamentos(self, move_line_id, journal_id, caixa, valor, cod_forma, juros):
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
   
    def insere_pedido_integracao(self):
        # lê arquivos json recebido dos pedidos
        # verifica se o pedido ja foi incluido
        # gera um arquivo com todos os pedidos da sessao
        # pra ser enviado para o pdv evitando o envio dos 
        # arquivos que ja estao neste retorno
        
        path_file = '/var/www/webroot/arquivos'
        path_file_return = '/var/www/webroot/retornos/retorno.json'
        arquivos = os.listdir(path_file)
        # para cada arquivo na pasta
        num_arq = 1
        # lista_pedido = set()
        ses = 0
        for i in arquivos:
            if num_arq == 20:
                continue
            num_arq += 1
            nome_arq = i[:i.index('.')]
            # buscar pedido ja existe
            pos = self.env['pos.order']
            pedido = pos.search([('name', '=', nome_arq)])

            if pedido:
                # lista_pedido.add(nome_arq)
                # retorno.writelines(list(lista_pedido)+',')
                # Usando a sessao pra gerar o RETORNO
                ses = pedido.session_id
                os.remove(path_file + '/' + i)
                continue
            f = open(path_file + '/' + i, mode="r")
            ped = json.load(f)
            # if ped['name'] == '4561-163115':
            #     import pudb;pu.db
            session = self.env['pos.session']
            prt_obj = self.env['res.partner']
            prod_obj = self.env['product.product']
            session_name = f"-{str(ped['pos_session_id'])}"
            ses = session.search([('name', 'like', session_name)])
            if not ses:
                continue
            # for p_lancado in pedb_lancado:
            #     if p_lancado.state == 'draft':
            #         p_lancado.write({'amount_paid': ped.amount_paid})
            #         p_lancado.action_pos_order_paid()

            _logger.info(f"Inserido PEDIDO : {nome_arq}")
            vals = {}
            vals['name'] = ped['name']
            vals['session_id'] = ses.id
            # vals['date_order'] = datetime.strftime(ped['date_order'],'%Y-%m-%d %H:%M:%S')
            vals['date_order'] = ped['date_order'][:19]
            part = prt_obj.browse([ped['partner_id']])
            if part:
                vals['partner_id'] = part.id
            else:
                # f.write(f"############# - Cliente nao encontrado : {ped['partner_id']}")
                continue
            # dicionario felicita
            user = ped['user_id']
            if user == 40:
                user = 50
            # user = self.env['res.users'].browse([])
            # if user:
            #     vals['user_id'] = user.id
            # else:
            #     f.write(f"############## - User nao encontrado : {ped['user_id']}")
            #     continue
            # if ped.amount_total and not ped.amount_paid:
            #     continue
            
            vals['pos_reference'] = ped['pos_reference']
            vals['amount_tax'] = ped['amount_return']
            vals['amount_total'] = ped['amount_return']
            vals['amount_return'] = ped['amount_return']

            # Tem troca
            troca = 0.0
            for line_ids in ped['lines']:
                line = line_ids[2]
                if 'Troca' in line['name']:
                    troca += line['price_unit'] * line['qty']

            t_paid = 0.0
            for pg_ids in ped['statement_ids']:
                pg = pg_ids[2]
                t_paid += pg['amount']
            dif_pag = ped['amount_return'] - t_paid + troca

            desconto = 0.0
            if dif_pag > 0.009:
                desconto = round(dif_pag / ped['amount_return'] * 100, 2)
                if desconto < 0.01:
                    desconto = 0.0

            vals['amount_paid'] = t_paid
            vals['company_id'] = 1
            vals['pricelist_id'] = 1
            ped_id = pos.create(vals) 
            list_adi = []
            
            linhas = len(ped['lines'])
            desc_soma = dif_pag
            print('Inicio : %s' %str(desc_soma))
            for line_ids in ped['lines']:
                linhas -= 1
                line = line_ids[2]
                # prod = dest.env['product.product'].search([('default_code', '=', line.product_id.default_code)])
                # if not len(prod):
                #     #logger.info(f"ITEM nao encontrado : {line.product_id.default_code}")
                #     prod = dest.env['product.product'].search([('barcode', '=', line.product_id.barcode)])
                # if not len(prod):
                #if len(prod):
                #    print (f"ITEM : {line.product_id.default_code}")

                #TODO buscar pelo codigo nao id
                px = line['product_id']
                if px == 30979:
                    px = 30683
                if px == 31344:
                    px = 31242
                if px == 30430:
                    px = 30495
                if px == 29899:
                    px = 30586
                if px == 30406:
                    px = 30404
                # if 'Troca' in line['name']:
                #     troca += line['price_unit'] * line['qty']
                    # import pudb;pu.db
                sub_total = line['price_unit'] * line['qty']
                print('1-VALOR : %s' %str(sub_total))
                print('2-Reducao : %s' %str(sub_total * (desconto/100)))
                if linhas == 0:
                    desconto =  (desc_soma / sub_total) * 100
                    print('4-Desc Final : %s' %str(desconto))
                else:
                    desc_soma -= sub_total * (desconto/100)
                    print('3-total desc : %s' %str(desc_soma))
                sub_total = sub_total - (sub_total * (desconto/100))
                vals_item = {
                    "name": line['name'],
                    "product_id": px, 
                    "full_product_name" :line['name'],
                    "qty": line['qty'],
                    "price_unit": line['price_unit'],
                    "discount": desconto,
                    "tipo_venda": line['tipo_venda'],
                    "price_subtotal": sub_total,
                    "price_subtotal_incl": sub_total,
                }
                print('5-GERALLLLLLLLLLLLLL : %s' %str(sub_total))
                # if 'discount' in line:
                    # vals_item["discount"] = line['discount']
                # "order_id": ped_id.id,
                #import pudb;pu.db
                # ped_id.write({'lines'(vals_iten)
            
                list_adi.append(vals_item)
                # vals['lines'] = [(0, 0, list_adi)]
                ped_id.write({'lines': [(0, 0, vals_item)]})
            if troca or dif_pag:
                tot = ped_id.amount_total + troca - dif_pag
                print('Total GERAL XXXXXXXXXXXXXXXXXXX: %s' %(str(tot)))
                # import pudb;pu.db
                ped_id.write({
                    'amount_tax': tot,
                    'amount_total': tot,
                    'amount_return': tot,
                })
            #  aqui aba pagamento 
            list_pag = []
            metodo_pag = ''
            for pag_ids in ped['statement_ids']:
                pag = pag_ids[2]
                jrn = self.env['account.journal'].browse([pag['journal']])
                metodo_pag = self.env['pos.payment.method'].search([('name', 'ilike', jrn.name[:2])])
                # datetime.strftime(pag['date'],'%Y-%m-%d'),
                # "pos_order_id": ped_id.id,
                print('Total PAGO: %s' %(str(pag['amount'])))
                vals_pag = {
                    "name": pag['name'],                
                    "amount": pag['amount'],                     
                    "payment_method_id": metodo_pag.id,
                    "payment_date": pag['date'][:10],
                    "session_id": ses.id,
                }
                #import pudb;pu.db
                # list_pag.append(vals_pag)
                # vLine = b_pedidoPag.create(vals_pag)
                ped_id.write({'payment_ids': [(0, 0, vals_pag)]})
            # vals['payment_ids'] = [(0, 0, list_pag)]
            # ped_id = pos.create(vals) 
            # mudando o status pra pago
            if metodo_pag and metodo_pag.name[:2] != '4-':
                ped_id.action_pos_order_paid()

            # se a prazo criando a Fatura
            if metodo_pag.name[:2] == '4-':
                #import pudb;pu.db
                ped_id.write({'to_invoice': True})
                move_vals = ped_id._prepare_invoice_vals()
                new_move = ped_id._create_invoice(move_vals)
                ped_id.write({'account_move': new_move.id, 'state': 'invoiced'})
                new_move.sudo().with_company(ped_id.company_id)._post()
            
                # ver se esta paga

                # if ped.invoice_id.state == 'paid':
                # for ct in ped.invoice_id.receivable_move_line_ids:
                #     if ct.reconciled:
                #         bancos = origem.env['account.journal'].search([
                #             ('type', 'in', ('cash', 'bank'))])
                #         aml = origem.env['account.move.line'].search([
                #             ('ref','=',ped.name),
                #             ('journal_id', 'in', bancos)
                #         ])
                #         for ml in aml:
                #             aml_id = origem.env['account.move.line'].browse(ml)
                #             jrn = dest.env['account.journal'].search([('name', 'ilike', ml.journal_id.name[:2])])
                #             jrn_id = dest.env['account.journal'].browse(jrn)
                #             baixa_pagamentos(new_move, jrn_id, 0, aml_id.debit, 0, 0)
        if ses:
            # crio um arquivo com todos os pedidos desta sessao
            pedido_ses = self.env['pos.order'].search([('session_id', '=', ses.id)])
            pd = []
            for px in pedido_ses:
                px_ids = {}
                px_ids['session'] = px.session_id.id
                px_ids['order_id'] = px.id
                px_ids['codmovimento'] = px.name
                pd.append(px_ids)
            # if len(list(lista_pedido)):
            with open(path_file_return, 'w+') as tfile:
                # tfile.write(list(pd))

                for items in list(pd):
                    tfile.write('%s,' % items)
	            # tfile.write('\n'.join(list(lista_pedido)))
             
    # for ses in a_session.browse(a_ses): 
    #     #cli_id = b_cliente.search([('name', '=', cli.name)])
    #     #print ('Codigo : %s , Nome : %s.' % (cli.id,cli.name))
    #     #print ('Codigo odoo 14 : %s ' % (cli_id)) 
        
    #     pedidos_10 = a_pedido.search([('session_id', '=', ses.id)])
    #     pSession = b_session.search([('name', 'ilike', ses.name )])
    #     pSession_id = 0
    #     if not len(pSession):
    #         vals = {}
    #         user = a_user.search([('name', '=', ses.user_id.name)])
    #         vals['user_id'] = user[0]
    #         vals['name'] = ses.name
    #         vals['config_id'] = ses.config_id.id
    #         vals['start_at'] = datetime.strftime(ses.start_at,'%Y-%m-%d %H:%M:%S')
    #         if ses.stop_at:
    #             vals['stop_at'] = datetime.strftime(ses.stop_at,'%Y-%m-%d %H:%M:%S')
    #             vals['state'] = 'closed'    
    #         pSession_id = b_session.create(vals)
    #         pSes = b_session.browse(pSession_id)
    #         pSes.write({'name': ses.name})
    #         #logger.info(f"Inserido a sessão : {ses.name}")
    #     if pSession_id:
    #         pedidos_14 = b_pedido.search([('session_id', '=', pSession_id), ('state', '!=', 'draft')])
    #         pSes = b_session.browse([pSession_id])
    #     else:
    #         pedidos_14 = b_pedido.search([('session_id', '=', pSession[0]), ('state', '!=', 'draft')])
    #         pSes = b_session.browse(pSession)
    #     vals_update = {}
    #     if ses.state != pSes.state:
    #         vals_update['state'] = ses.state
    #     if ses.stop_at != pSes.stop_at:
    #         vals_update['stop_at'] = datetime.strftime(ses.stop_at,'%Y-%m-%d %H:%M:%S')
    #     if len(vals_update):
    #         pSes.write(vals_update)
        

    #     if len(pedidos_10) == len(pedidos_14):
    #         continue
    #     #import pudb;pu.db
    #     #logger.info(f"Sessão : {ses.name}")
    #     if len(pSession):
    #         insere_pedido(pSes.id,ses.id)
    #         continue     

    #     #insere_pedido(pSession_id,ses.id)   
    