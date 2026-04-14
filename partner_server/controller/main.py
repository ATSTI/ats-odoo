
# -*- coding: utf-8 -*-
#
#    Copyright © 2019–; Brasil; IT Brasil; Todos os direitos reservados
#    Copyright © 2019–; Brazil; IT Brasil; All rights reserved
#
from datetime import datetime, timedelta
import logging
from unicodedata import normalize
from odoo import http
from odoo.http import request
logger = logging.getLogger(__name__)



class ConsultaPendencia(http.Controller):

    @http.route('/consultar-pendencia', type='json', auth="user", csrf=False)
    def website_consultar_pendencia(self, company_name, **kwargs):
        env = request.env
        cmp_name = normalize('NFKD', company_name).encode('ASCII', 'ignore').decode('ASCII')
        partner = env['res.partner'].search([('name', 'ilike', cmp_name)])
        if not partner:
            return {"error": "Parceiro não encontrado."}

        hoje = datetime.now()
        inicio = hoje.replace(day=1)
        proximo_mes = (inicio + timedelta(days=32)).replace(day=1)
        fim = proximo_mes - timedelta(days=1)

        pendencias = env['account.move'].search([
            ('partner_id', '=', partner.id), 
            ('state', '=', 'posted'), 
            ('payment_state', '!=', 'paid'),
            ('invoice_date', '>=', inicio),
            ('invoice_date', '<=', fim)
        ])
        pendencias_data = []
        for move in pendencias:
            pendencias_data.append({
                'move_id': move.id,
                'move_name': move.name,
                'amount_total': move.amount_total,
                'currency_id': move.currency_id.name,
                'date': move.line_ids[0].date_maturity.strftime('%Y-%m-%d') if move.line_ids[0].date_maturity else None,
            })
        return {"pendencias": pendencias_data}