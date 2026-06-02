
# -*- coding: utf-8 -*-
#
#    Copyright © 2019–; Brasil; IT Brasil; Todos os direitos reservados
#    Copyright © 2019–; Brazil; IT Brasil; All rights reserved
#

import logging
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from unicodedata import normalize
import re
from odoo import http, fields
from odoo.http import request
from math import floor

logger = logging.getLogger(__name__)



class IntegracaoPdv(http.Controller):

    @http.route('/nfe', type='json', auth="user", csrf=False)
    def website_nfe(self, **kwargs):
        data = request.params
        num_nota = len(data)
        order = http.request.env['sale.order']
        cliente = http.request.env['res.partner']
        user_id = http.request.env['res.users'].browse([request.uid])
        # crio uma lista com CNPJs unicos
        lista_cnpj = set()
        lista_notas = []
        while num_nota > 0:
            #print (f" ---- Nota {num_nota} -----------")
            chave = str(num_nota)
            cnpj_emitente = data[chave]['empresa_cnpj']
            data_nota = data[chave]['nota_data']
            database = data[chave]['db']
            cnpj = re.sub('[^0-9]', '', cnpj_emitente)
            cnpj = '%s.%s.%s/%s-%s' %(cnpj[:2],cnpj[2:5],cnpj[5:8],cnpj[8:12],cnpj[12:14])
            dados_cli = {
                'nome': data[chave]['empresa_nome'],
                'cnpj': cnpj,
                'numero': data[chave]['numero'],
                'nota_data': data[chave]['nota_data'],
                'operacao': data[chave]['operacao'],
            }
            lista_cnpj.add(cnpj)
            lista_notas.append(dados_cli)
            num_nota -= 1
        print("montado lista_cnpj e lista_notas")
        list_cnpj = list(lista_cnpj)
        # criar lista do financeiro
        lista_financeiro = set()
        for lista in list_cnpj:
            print (f" ---- fazendo  {cnpj} -----------")
            cnpj = lista
            cli_ids = cliente.sudo().search([('vat', '=', cnpj),])
            # se cliente tem financeiro, cobranca e dele
            if cli_ids.financeiro:
                lista_financeiro.add(cli_ids.financeiro.id)
            else:
                for emp in lista_notas:
                    if cnpj == emp['cnpj']:
                        nome_emp = emp['nome']
                print(f"@@@@@@@@@@@@@@@@  sem financeiro : {cnpj} - {nome_emp} --- {database} --  @@@@@@@@@@@@@@@@@@")
                continue

            data_pedido = datetime.strptime(data_nota, "%Y-%m-%d %H:%M:%S")
            data_pedido = data_pedido + relativedelta(months=1)
            data_pedido = data_pedido.replace(day=1, hour=3, minute=59, second=0, microsecond=0)
            
            #('state', '=', 'draft'),
            # mes_ano = f"{str(data_pedido.month).zfill(2)}-{data_pedido.year}"
            mes_ano = f"{data_pedido.year}-{str(data_pedido.month).zfill(2)}"
            order_id = order.sudo().search([
                ('partner_id', '=', cli_ids.financeiro.id),
                ('client_order_ref', '=', mes_ano),
                ], limit=1)
            if not order_id:
                print ("########### - criando pedido - ############")
                # crio o pedido
                if cli_ids.financeiro.user_id:
                    usuario = cli_ids.financeiro.user_id.id
                else:
                    usuario = user_id.id
                vals = {
                    'partner_id': cli_ids.financeiro.id,
                    'date_order': data_pedido,
                    'origin': 'produtor',
                    'client_order_ref': mes_ano,
                    'user_id': usuario,
                }
                order_id = order.create(vals)
                # cnpj = '%s.%s.%s/%s-%s' %(cnpj[:2],cnpj[2:5],cnpj[5:8],cnpj[8:12],cnpj[12:14])
                #emitente = f"{cnpj} - {lista['nome']}"
            if order_id:
                emitente = ""
                emitente_notas = ""
                cnpj_inserir = False
                for emitido in lista_notas:
                    if cnpj != emitido["cnpj"]:
                        continue
                    if not emitente:
                        emitente += f"{cnpj} - {emitido['nome']}"
                    if cnpj == emitido["cnpj"]:
                        emitente_notas += f" {emitido['numero']},"
                        #print (f"inserindo linha no pedido {cnpj}")
                    cnpj_inserir = True
                if cnpj_inserir:
                    # verificar se cnpj ja inserido na linha
                    order_line = []
                    #nao_incluido = True
                    vals_line = []
                    if not order_id.order_line:
                        print (f"inserindo linha {cnpj} - {emitente_notas}")
                        vals_line = {
                            'name': emitente + ', Notas:' + emitente_notas,
                            'product_id': 60,
                            'product_uom_qty': 1,
                            'price_unit': 1,
                        }
                        order_line.append((0, 0,vals_line))
                    else:
                        existe = False
                        for line in order_id.order_line:
                            if not emitente:
                                continue
                            if cnpj in line.name:
                                existe = True
                                continue
                        if not existe:
                            print (f"inserindo linha {cnpj} - {emitente_notas}")
                            vals_line = {
                                'name': emitente + ', Notas:' + emitente_notas,
                                'product_id': 60,
                                'product_uom_qty': 1,
                                'price_unit': 1,
                            }
                            order_line.append((0, 0,vals_line))
                    emitente = ""
                    emitente_notas = ""
                    # order_id.sudo().write(vals_line)
                    if len(order_line):
                        order_id['order_line'] = order_line

        ## criando ou alterando pedidos
        #for fin in lista_financeiro:
        #    # procura se existe um pedido de venda, deste financeiro
        #    data_pedido = datetime.strptime(data_nota, "%Y-%m-%d %H:%M:%S")
        #    data_pedido = data_pedido + relativedelta(months=1)
        #    data_pedido = data_pedido.replace(day=1, hour=3, minute=59, second=0, microsecond=0)

        #    order_id = order.sudo().search([
        #        ('partner_id', '=', fin),
        #        ('date_order', '=', data_pedido),
        #        ('state', '=', 'draft'),
        #        ], limit=1)
        #    if not order_id:
        #        # crio o pedido
        #        vals = {
        #            'partner_id': fin,
        #            'date_order': data_pedido,
        #            'origin': 'produtor',
        #        }
        #        order_id = order.sudo().create(vals)
        #    for lista in list_cnpj:
        #        cnpj = lista
        #        # cnpj = '%s.%s.%s/%s-%s' %(cnpj[:2],cnpj[2:5],cnpj[5:8],cnpj[8:12],cnpj[12:14])
        #        #emitente = f"{cnpj} - {lista['nome']}"
        #        emitente = ""
        #        emitente_notas = ""
        #        for emitido in lista_notas:
        #           if not emitente:
        #               emitente += f"{cnpj} - {emitido['nome']}"
        #           if cnpj == emitido["cnpj"]:
        #               emitente_notas += f" {emitido['numero']}-{emitido['nota_data']}-{emitido['operacao']},\n"
        #        # verificar se cnpj ja inserido na linha
        #        order_line = []
        #        nao_incluido = Trueaaaa
        #        for line in order_id.order_line:
        #            if cnpj in line.name:
        #                nao_incluido = False
        #                continue
        #        if nao_incluido:
        #            vals_line = {
        #                'name': emitente + ', Notas:' + emitente_notas,
        #                'product_id': 60,
        #                'qty': 1,
        #                'price_unit': 1,
        #            }
        #            # order_id.sudo().write(vals_line)
        #            order_line.append((0, 0,vals_line))
        #            order_id['order_line'] = order_line
    
    #BUSCANDO RESPONSAVEL FINANCEIRO
    @http.route('/check-pending-payments', type='http', auth="public", csrf=False)
    def website_check_pending_payments(self, company_name=None, company_vat=None, **kwargs):
        if not company_name:
            return request.make_json_response({"error": "company_name é obrigatório"}, status=400)

        env = request.env
        company = request.env.company
        cmp_name = normalize('NFKD', company_name).encode('ASCII', 'ignore').decode('ASCII')
        partner = env['res.partner'].sudo().search(['|', ('name', 'ilike', cmp_name),('cnpj_cpf_stripped', '=', company_vat)], limit=1)
        if not partner:
            return request.make_json_response({"error": "Parceiro não encontrado."}, status=404)
        
        dependentes = env['res.partner']

        if partner.financeiro:
            dependentes = env['res.partner'].sudo().search([
                ('financeiro', '=', partner.financeiro.id)
            ])

        parceiros = dependentes if dependentes else partner

        hoje = fields.Date.today()
        inicio = hoje.replace(day=1)
        proximo_mes = (inicio + timedelta(days=32)).replace(day=1)
        fim = proximo_mes - timedelta(days=1)    
        
        pendencias = env['account.move'].sudo().search([
            ('partner_id', 'in', parceiros.ids), 
            ('state', '=', 'posted'), 
            ('payment_state', '!=', 'paid'),
            ('invoice_date_due', '>=', inicio),
            ('invoice_date_due', '<=', fim),
            ('move_type', 'in', ['out_invoice', 'out_refund']),
        ])
        
        company_names = [{'name': prt.name} for prt in parceiros]
    
        pendencias_data = []
    
        # Custom Message
        if company.notify and company.notify_customers:
            pendencias_data.append({
                'company_names': company_names,
                'pending': False,
                'mensagem': company.notify_customers,
            })

            return request.make_json_response({
                "pendencias": pendencias_data
            })
        
        #Check pending
        for move in pendencias:
            if not move.invoice_date_due:
                continue

            date_due_limit = move.invoice_date_due + timedelta(
                days=company.days_to_notify
            )

            msg = ""
            if hoje >= move.invoice_date_due and hoje < date_due_limit:
                dias_restantes = (date_due_limit - hoje).days
                msg = (
                    f"Por favor, contate o financeiro da ATS, "
                    f"whatsapp: {company.mobile}\n"
                    f"Seu sistema será interrompido em "
                    f"{dias_restantes} dia(s)"
                )

            elif hoje >= date_due_limit:
                msg = (
                    f"Por favor, contate o financeiro da ATS, "
                    f"whatsapp: {company.mobile}\n"
                    f"SEU SISTEMA ESTÁ BLOQUEADO!!!"
                )
            if msg:
                pendencias_data.append({
                    'company_names': company_names,
                    'pending': True,
                    'mensagem': msg,
                })

        if not pendencias_data:
            pendencias_data.append({
                'company_names': company_names,
                'pending': False,
                'mensagem': '',
            })

        return request.make_json_response({
            "pendencias": pendencias_data
        })
