
# -*- coding: utf-8 -*-
#
#    Copyright © 2019–; Brasil; IT Brasil; Todos os direitos reservados
#    Copyright © 2019–; Brazil; IT Brasil; All rights reserved
#
from datetime import datetime, timedelta
import logging
from unicodedata import normalize
from odoo import http, fields
from odoo.http import request
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)



class ConsultaPendencia(http.Controller):

    @http.route('/check-pending-payments', type='http', auth="public", csrf=False)
    def website_check_pending_payments(self, company_name=None, company_vat=None, **kwargs):
        if not company_name:
            return request.make_json_response({"error": "company_name é obrigatório"}, status=400)

        env = request.env
        cmp_name = normalize('NFKD', company_name).encode('ASCII', 'ignore').decode('ASCII')
        partner = env['res.partner'].sudo().search(['|', ('name', 'ilike', cmp_name),('cnpj_cpf_stripped', '=', company_vat)], limit=1)
        if not partner:
            return {"error": "Parceiro não encontrado."}

        hoje = datetime.now()
        inicio = hoje.replace(day=1)
        proximo_mes = (inicio + timedelta(days=32)).replace(day=1)
        fim = proximo_mes - timedelta(days=1)

        pendencias = env['account.move'].sudo().search([
            ('partner_id', '=', partner.id), 
            ('state', '=', 'posted'), 
            ('payment_state', '!=', 'paid'),
            ('invoice_date', '>=', inicio),
            ('invoice_date', '<=', fim),
            ('invoice_date_due', '<=', fields.Date.today())
        ])
        pendencias_data = []
        for move in pendencias:
            date_now = fields.Date.today()
            date_due_limit = move.invoice_date_due + timedelta(days=3)
            msg = ""
            if date_now < date_due_limit:
                msg = f"""Não verificamos o seu pagamento. Por favor, contate o financeiro, whatsapp: 1997104-0941\n
                   Seu sistema será bloqueado em {(date_due_limit - date_now).days} dia(s)"""
            if date_now >= date_due_limit:
                msg = f"""Não verificamos o seu pagamento. Por favor, contate o financeiro, whatsapp: 1997104-0941\n
                   SEU SISTEMA ESTÁ BLOQUEADO!!!"""
            if msg:
                pendencias_data.append({
                    'pending': True,
                    'mensagem': msg,
                })
        return request.make_json_response({
                "pendencias": pendencias_data
            })