# -*- coding:utf-8 -*-

from odoo import models, fields, api, tools, _
# from odoo.addons.point_of_sale.wizard.pos_box import PosBox
# from odoo.exceptions import UserError
from datetime import datetime, date, timedelta
# from unidecode import unidecode
import logging
# import psycopg2
import os
import fnmatch
import json
import odoorpc

# from . import atscon as con


_logger = logging.getLogger(__name__)
path_file = '/opt/odoo/arquivos'
path_file_return = '/opt/odoo/retornos/retorno.json'

class PosSession(models.Model):
    _inherit = 'pos.session'

    def excluir_pedido_pos(self, pos_id, pos_cx):
        pos = self.env['pos.order'].browse([pos_id])
        if pos.session_id.id == pos_cx:
            for pay in pos.payment_ids:
                pay.unlink()
            # for pick in pos.picking_ids:    
                # wiz = self.env['stock.return.picking']
                # pick_new = wiz._create_returns(pick)
                # pk = self.env['stock.picking'].browse([pick_new])
                #back = pick._create_backorder()
                #pick.button_validate()
            pos.write({'state': 'cancel'})

    def produto_corrige_ncm(self):
        origem = odoorpc.ODOO('url', port=8069)
        origem.login('url', 'user', 'password')
        a_prod = origem.env['product.product']
        b_prod = self.env['product.product']
        arq = open('/var/www/webroot/ncm_nao_encontrado.txt', '+r')
        itens = []
        for item in arq.readlines():
            itens.append(int(item.strip()))
        prod_b = b_prod.search([('ncm_id', '=', False), ('type', '=', 'product'), ('id', 'not in', itens)], order="id", limit=100)
        prod_a = a_prod.browse(prod_b._ids)
        arqx = open('/var/www/webroot/ncm_nao_encontrado.txt', '+a')
        for prd in prod_a:
            prod = b_prod.search([('default_code', '=', prd.default_code)])
            if prod:
                ncm = prd.product_tmpl_id.fiscal_classification_id.code
                if not ncm:
                    continue
                pr_ncm = self.env['l10n_br_fiscal.ncm'].search([('code', '=', ncm)])
                if not pr_ncm:
                    pr_ncm = self.env['l10n_br_fiscal.ncm'].search([('code', 'ilike', ncm[:7])], limit=1)
                if pr_ncm:
                    #_logger.info(f"ITEM : {prod.default_code}")
                    vp = {}
                    fiscal_genre_id = self.env["l10n_br_fiscal.product.genre"].search([("code", "=", ncm[0:2])])
                    vp['ncm_id'] = pr_ncm[0]
                    if fiscal_genre_id:
                        vp['fiscal_genre_id'] = fiscal_genre_id[0]
                    if not prod.fiscal_type:
                        vp['fiscal_type'] = '00'
                    if not prod.icms_origin:
                        vp['icms_origin'] = '0'
                    if len(vp):
                        prod.write(vp)
                else:
                    _logger.info(f"NCM nao encontrado : {ncm}, produto {prd.default_code}")
                    if prod.id not in itens:
                        arqx.write(str(prod.id) + '\n')
                    continue
        arq.close()
        arqx.close()
    
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
   
    def insere_caixa_integracao(self):
        # lê arquivos na pasta
        # path_file = '/var/www/webroot/arquivos'
        # path_file_return = '/var/www/webroot/retornos/retorno.json'
        # arquivos = os.listdir(path_file)
        arquivos = sorted(fnmatch.filter(os.listdir(path_file), "cai_*.json"))
        # para cada arquivo na pasta
        num_arq = 1
        user_adic = []
        for i in arquivos:
            # nome_arq = i[:i.index('.')]
            # if nome_arq[:4] != 'cai_POS_':
            #     continue
            # if num_arq == 20:
            #     continue
            num_arq += 1

            # buscar pedido ja existe
            ses = self.env['pos.session']
            f = open(path_file + '/' + i, mode="r")
            arq = json.load(f)

            # caixa = f"-{nome_arq[:6]}"
            caixa = f"-{arq['caixa']}"
            session = ses.search([('name', 'like', caixa)])
            state = arq["state"]
            if session:
                sesd = []
                for px in session:
                    if px.state == "opened" and state == "closed":
                        px.action_pos_session_closing_control()
                    if px.state == "closing_control" and state == "closed":
                        px._validate_session()
                    else:    
                        px_ids = {}
                        px_ids['tipo'] = 'sessao'
                        px_ids['user_id'] = px.user_id.id
                        px_ids['name'] = px.name
                        caixa = px.name[px.name.find('-')+1:]
                        px_ids['caixa'] = caixa
                        sesd.append(px_ids)
                with open(path_file_return, 'a+') as tfile:
                    for items in list(sesd):
                        tfile.write('%s,' % items)

                os.remove(path_file + '/' + i)
                continue
            vals = {}
            # vals["name"] = arq["name"]
            vals["start_at"] = arq["start_at"]
            usuario = self.env['res.users'].browse(arq["user_id"])
            vals["user_id"] = usuario.id
            if usuario.id in user_adic:
                continue
            user_adic.append(usuario.id)
            session_open = ses.search([('user_id', '=', usuario.id), ('state', '=', 'opened')])
            if session_open:
                # if state == "closed":
                    # session_open.action_pos_session_closing_control()
                continue
            pv = self.env['pos.config'].search([('name', 'ilike', usuario.name)], limit=1)
            ses_id = []
            if pv:
                vals['config_id'] = pv.id
                ses_id = ses.create(vals)
                if ses_id:
                    caixa = f"{ses_id.name}{caixa}"
                    ses_id.write({"name": caixa})
                    ses_id.set_cashbox_pos(0.0, '')
  
            sesd = []
            for px in ses_id:
                px_ids = {}
                px_ids['tipo'] = 'sessao'
                px_ids['user_id'] = px.user_id.id
                px_ids['name'] = px.name
                caixa = px.name[px.name.find('-')+1:]
                px_ids['caixa'] = caixa
                sesd.append(px_ids)
            # if len(list(lista_pedido)):
            with open(path_file_return, 'a+') as tfile:
                # tfile.write(list(pd))
                for items in list(sesd):
                    tfile.write('%s,' % items)

    def insere_pedido_integracao(self):
        # lê arquivos json recebido dos pedidos
        # verifica se o pedido ja foi incluido
        # gera um arquivo com todos os pedidos da sessao
        # pra ser enviado para o pdv evitando o envio dos 
        # arquivos que ja estao neste retorno
        # path_file = '/var/www/webroot/arquivos'
        # path_file_return = '/var/www/webroot/retornos/retorno.json'
        # arquivos = os.listdir(path_file)
        arquivos = fnmatch.filter(os.listdir(path_file), "ped_*.json")
        # para cada arquivo na pasta
        num_arq = 1
        # lista_pedido = set()
        ses = 0
        for i in arquivos:
            nome_arq = i[:i.index('.')][4:]
            # if nome_arq[:4] != 'ped_':
            #     continue
            if num_arq == 50:
                continue
            num_arq += 1
            
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
            cli_n = ped['nomecliente']
            if ped['nomecliente'] == 'Cliente do Sistema':
                cli_n = 'Consumidor'
            prt = prt_obj.search([('name', 'ilike', cli_n)], limit=1)
            if not prt:
                prt = prt_obj.search([('id', '=', ped['partner_id'])])
            if prt:
                vals['partner_id'] = prt.id
            else:
                # f.write(f"############# - Cliente nao encontrado : {ped['partner_id']}")
                print(f"############# - Cliente nao encontrado : {ped['nomecliente']}")
                continue
            # dicionario felicita
            user = ped['user_id']
            user_id = self.env['res.users'].search([('id', '=', user)])
            if user_id:
                if user == 40:
                    user_id = self.env['res.users'].browse([50])
                vals['user_id'] = user_id.id
            else:
                vals['user_id'] = ses.user_id.id
            
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
            try:
                ped_id = pos.create(vals)
            except Error as e:
                ses.message_post(
                    body=_(
                        "ERRO para inserir pedido %s, Erro %s"
                    ) % (ped['name'], e.pgerror)
                )               
            list_adi = []
            
            linhas = len(ped['lines'])
            desc_soma = dif_pag
            # print('Inicio : %s' %str(desc_soma))
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
                codpro = str(line['product_id'])
                prd = prod_obj.search([('default_code', '=', codpro)])
                descricao  = line['name']
                if not prd:
                    prd = prod_obj.search([('name', 'ilike', line['name'])], limit=1)
                    if len(line['product_id']) < 10 and not prd:
                        prd = prod_obj.search([('id', '=', line['product_id'])])
                    if not prd:
                        prd = prod_obj.search([('default_code', '=', '321')])
                        descricao = f"{descricao} - PRODUTO NAO LOCALIZADO"
                #TODO buscar pelo codigo nao id
                # px = line['product_id']
                # if px == 30979:
                #     px = 30683
                # if px == 31344:
                #     px = 31242
                # if px == 30430:
                #     px = 30495
                # if px == 29899:
                #     px = 30586
                # if px == 30406:
                #     px = 30404
                # if px == 30406:
                #     px = 30404
                # if 'Troca' in line['name']:
                #     troca += line['price_unit'] * line['qty']
                sub_total = line['price_unit'] * line['qty']
                # print('1-VALOR : %s' %str(sub_total))
                # print('2-Reducao : %s' %str(sub_total * (desconto/100)))
                if linhas == 0:
                    desconto = 0.0
                    if sub_total:
                        desconto =  (desc_soma / sub_total) * 100
                    # print('4-Desc Final : %s' %str(desconto))
                else:
                    desc_soma -= sub_total * (desconto/100)
                    # print('3-total desc : %s' %str(desc_soma))
                sub_total = sub_total - (sub_total * (desconto/100))
                vals_item = {
                    "name": descricao, 
                    "product_id": prd.id, 
                    "full_product_name" :line['name'],
                    "qty": line['qty'],
                    "price_unit": line['price_unit'],
                    "discount": desconto,
                    "tipo_venda": line['tipo_venda'],
                    "price_subtotal": sub_total,
                    "price_subtotal_incl": sub_total,

                }
                # print('5-GERALLLLLLLLLLLLLL : %s' %str(sub_total))
                # if 'discount' in line:
                    # vals_item["discount"] = line['discount']
                # "order_id": ped_id.id,
                # ped_id.write({'lines'(vals_iten)
     
                list_adi.append(vals_item)
                ped_id.write({'lines': [(0, 0, vals_item)]})
            if troca or dif_pag:
                tot = ped_id.amount_total + troca - dif_pag
                # print('Total GERAL XXXXXXXXXXXXXXXXXXX: %s' %(str(tot)))
                ped_id.write({
                    'amount_tax': tot,
                    'amount_total': tot,
                    'amount_return': tot,
                })
            #  aqui aba pagamento 
            list_pag = []
            metodo_pag = ''
            falha_pag = True
            for pag_ids in ped['statement_ids']:
                pag = pag_ids[2]
                if pag['journal'] in ('R-', 'S-','U-'):
                    continue
                jrn = self.env['account.journal'].search([('name', 'like', pag['journal'])])
                if not jrn:
                    ses.message_post(
                        body=_(
                            "ERRO DIARIO NAO ENCONTRADO: %s - %s"
                        ) % (ped['name'], pag['journal'])
                    )
                    falha_pag = False
                    continue 
                metodo_pag = self.env['pos.payment.method'].search([('name', 'ilike', jrn.name[:2])])
                # datetime.strftime(pag['date'],'%Y-%m-%d'),
                # "pos_order_id": ped_id.id,
                # print('Total PAGO: %s' %(str(pag['amount'])))
                vals_pag = {
                    "name": pag['name'],                
                    "amount": pag['amount'],                     
                    "payment_method_id": metodo_pag.id,
                    "payment_date": pag['date'][:10],
                    "session_id": ses.id,
                }
                # list_pag.append(vals_pag)
                # vLine = b_pedidoPag.create(vals_pag)
                ped_id.write({'payment_ids': [(0, 0, vals_pag)]})
            if metodo_pag and metodo_pag.name[:2] != '4-' and falha_pag:
                ped_id.action_pos_order_paid()
            # se a prazo criando a Fatura
            if metodo_pag and metodo_pag.name[:2] == '4-':
                ped_id.write({'to_invoice': True})
                move_vals = ped_id._prepare_invoice_vals()
                new_move = ped_id._create_invoice(move_vals)
                ped_id.write({'account_move': new_move.id, 'state': 'invoiced'})
                new_move.sudo().with_company(ped_id.company_id)._post()
            
            ped_id._create_order_picking()
            
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
                px_ids['tipo'] = 'pedido'
                px_ids['caixa'] = px.session_id.id
                px_ids['order_id'] = px.id
                px_ids['codmovimento'] = px.name
                px_ids['user_id'] = px.user_id.id
                pd.append(px_ids)
            # if len(list(lista_pedido)):
            with open(path_file_return, 'w') as tfile:
                # tfile.write(list(pd))

                for items in list(pd):
                    tfile.write('%s,' % items)

    def insere_devolucao_integracao(self):
        # arquivos = os.listdir(path_file)
        arquivos = fnmatch.filter(os.listdir(path_file), "dev_*.json")
        # para cada arquivo na pasta
        num_arq = 1
        for i in arquivos:
            nome_arq = i[:i.index('.')][4:]
            if num_arq == 50:
                continue
            num_arq += 1           
            # buscar pedido ja existe
            pick = self.env['stock.picking']
            picking = pick.search([('name', '=', nome_arq)])

            if picking:
                os.remove(path_file + '/' + i)
                continue
            f = open(path_file + '/' + i, mode="r")
            p = json.load(f)
            user_id = self.env['res.users'].browse([p['user_id']])
            # nome_busca = str(p['origin'])
            # dev = pick.sudo().search([
            #             ('origin', 'like', nome_busca)
            #         ]) 
            item = []
            vals = {}            
            for lines in p['move_lines']:
                line = lines[2]
                vals['origin'] = str(p['origin'])
                vals['name'] = nome_arq
                operacao = self.env['stock.picking.type'].sudo().search([
                    ('name', 'ilike', 'devolucao')
                ])
                prd = {}
                for tipo in operacao:
                    if tipo.warehouse_id.company_id.id == user_id.company_id.id:
                        # tipo_operacao = tipo
                        vals['picking_type_id'] = tipo.id
                        vals['location_id'] = tipo.default_location_src_id.id
                        vals['location_dest_id'] = tipo.default_location_dest_id.id
                        vals['note'] = p['motivo'] 
                        prd['location_id'] = tipo.default_location_src_id.id
                        prd['location_dest_id'] = tipo.default_location_dest_id.id
                prod = self.search([('default_code', '=', line['product_code'])])
                if not prod:
                    prod = self.search([('name', 'ilike', line['name'])], limit=1)
                prd['product_id'] =  prod.id
                prd['product_uom_qty'] = line['qty_done'] 
                prd['product_uom'] = prod.uom_id.id
                prd['quantity_done'] = line['qty_done'] 
                prd['name'] = line['name']               
                item.append((0, 0,prd))
                vals['move_ids_without_package'] = item

                pos = self.env['stock.picking']
                pick = pos.sudo().create(vals)
                pick.action_confirm()
                pick.action_assign()            
                pick.button_validate()

    def insere_sangria(self):
        arquivos = sorted(fnmatch.filter(os.listdir(path_file), "san_*.json"))
        # para cada arquivo na pasta
        num_arq = 1
        user_adic = []
        for i in arquivos:
            f = open(path_file + '/' + i, mode="r")
            lt = json.load(f)

            # caixa = f"-{nome_arq[:6]}"
            caixa = f"-{lt['caixa']}"
            sg_obj = self.env['account.bank.statement.line']
        
            # vejo os diarios usados no PDV do Caixa aberto       
            session = self.env['pos.session'].sudo().search([('name', 'ilike', caixa)])
            if not session:
                continue
            
            lista_st = []
            for lt_st in session.statement_ids:
                lista_st.append(lt_st.id)

            motivo = lt['motivo']
            valor = lt['amount']
            cod_forma = lt['name']
            cod_venda = int(lt['cod_venda'])
            
            diario = '1-'
            if cod_venda == 2: 
                diario = motivo[:2]
            diario_obj = self.env['account.journal']    
            diario_id = diario_obj.search([
                ('company_id', '=', session.user_id.company_id.id),
                ('name', 'ilike', diario)])
            # verifica se ja foi feito
            #line = sg_obj.search([
            #    ('ref', '=', str(cod_forma)),
            #    ('statement_id', 'in', (lista_st)),
            #])
            ja_importou = self.env['account.bank.statement.line'].search([
                ('name', '=', str(cod_forma)+caixa)])
            if not ja_importou:
                arp = self.env['account.payment.register']
                arp.lanca_sangria_reforco(diario_id, caixa, valor, cod_forma, cod_venda, session.user_id.partner_id, motivo)
            else:
                os.remove(path_file + '/' + i)

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
    #     #logger.info(f"Sessão : {ses.name}")
    #     if len(pSession):
    #         insere_pedido(pSes.id,ses.id)
    #         continue     

    #     #insere_pedido(pSession_id,ses.id)   
    
