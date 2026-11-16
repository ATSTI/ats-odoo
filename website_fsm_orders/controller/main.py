from odoo import http, fields
from odoo.http import request
from datetime import datetime, timedelta


class WebsiteCalendarView(http.Controller):

    @http.route(['/agenda/eventos'], type='json', auth='user', website=True)
    def agenda_eventos(self, **kwargs):
        user = request.env.user

        agora = datetime.now()
        inicio = agora.replace(hour=0, minute=0, second=0, microsecond=0)
        fim = inicio + timedelta(days=30)

        fsm_orders = request.env['fsm.order'].search([
            ('person_id.partner_id', 'in', [user.partner_id.id]),
            ('scheduled_date_start', '>=', fields.Datetime.to_string(inicio)),
            ('scheduled_date_start', '<=', fields.Datetime.to_string(fim)),
        ], order='scheduled_date_start asc', limit=100)

        resultado = []
        for fo in fsm_orders:
            if not fo.scheduled_date_start or not fo.scheduled_date_end:
                continue

            try:
                start_dt = fields.Datetime.context_timestamp(fo, fo.scheduled_date_start)
                stop_dt = fields.Datetime.context_timestamp(fo, fo.scheduled_date_end)
            except Exception:
                start_dt = fo.scheduled_date_start
                stop_dt = fo.scheduled_date_end

            start_str = start_dt.strftime('%Y-%m-%d %H:%M:%S')
            end_str = stop_dt.strftime('%Y-%m-%d %H:%M:%S')

            loc = fo.location_id
            partes = [loc.street, loc.street2, loc.city, loc.state_id.name, loc.zip]
            endereco = ', '.join(p for p in partes if p)


            resultado.append({
                'id': fo.id,
                'title': fo.name,
                'start': start_str,
                'end': end_str,
                'allDay': False,
                'location': fo.location_id.name or '',
                'description': fo.description or '',
                'endereco': endereco,
            })

        return resultado

    @http.route(['/minha-agenda'], type='http', auth='user', website=True)
    def exibir_pagina_agenda(self, **kwargs):
        return request.render('website_fsm_orders.website_agenda_page')