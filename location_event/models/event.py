# -*- coding: utf-8 -*-

import datetime
from odoo import _,fields, api, models
from odoo.exceptions import UserError
from pytz import timezone
import pytz
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

class EventEvent(models.Model):
    _inherit = "event.event"

    product_id = fields.Many2one('product.product', string='Produto', index=True)
    qty = fields.Float(string='Duração em horas')

    #('id', '!=', False),
    def tem_evento(self, date_begin, date_end, product_id, event_id):
        """
        evento = self.env['event.event'].search([
            ('id', 'not in', [False, self.id]),
            ('state', 'in', ['draft', 'confirm']),
            ('date_begin', '<=', self.date_end),
            ('date_begin', '>=', self.date_begin),
            '|',
            ('date_end', '>', self.date_end),
            ('date_end', '<', self.date_begin),
            ('product_id', '=', self.product_id.id)
        ])
        """
        """str_sql = ''' \
            SELECT id \
            FROM event_event \
            WHERE (date_begin < '%s' and '%s' < date_end) \
                AND product_id=%s \
                AND id <> %s''' \
            %(date_end, date_begin, product_id, event_id)
        """
        self.env.cr.execute('''
            SELECT id
            FROM event_event
            WHERE (date_begin < %s and %s < date_end)
                AND product_id=%s
                AND id <> %s''',
            (date_end, date_begin, product_id, event_id))
        qry = self.env.cr.fetchall()    
        #if qry:
        #    return True
        #else:
        # 30/06/2018 tirei isto pois, um curso pode ir o mes de julho inteiro, e em outros dias de julho ter outros cursos
        return False
        #if any((((line.date_end > self.date_begin and line.date_begin < self.date_begin) or (
        #        line.date_end > self.date_end and line.date_begin < self.date_end) or (
        #        line.date_end < self.date_end and line.date_begin > self.date_begin)) and line.id != self.id) and line.product_id.id == self.product_id.id
        #       for line in evento):



    @api.onchange('product_id')
    def _onchange_product_id(self):
        #if self.tem_evento(self.date_begin, self.date_end, self.product_id):
        #    raise UserError('Existe um evento ocorrendo neste horário')
        #else:
        self.name = self.product_id.name
        if self.product_id.company_id:
            self.address_id = self.product_id.company_id.partner_id.id
            #self.name

    @api.onchange('date_begin')
    def _onchange_date_begin(self):
        if self.date_end:
            self.qty = self.set_duration()

    @api.onchange('date_end')
    def _onchange_date_end(self):
        if self.date_begin:
            self.qty = self.set_duration()

    def set_duration(self):
        date_begin = datetime.datetime.strptime(self.date_begin, '%Y-%m-%d %H:%M:%S')
        date_end = datetime.datetime.strptime(self.date_end, '%Y-%m-%d %H:%M:%S')
        dur = date_end - date_begin
        duration = dur.days * 24
        duration += float(dur.seconds)/3600
        return duration

    @api.multi
    def write(self, vals):
        #evento = self.env['event.event'].search([('id', '!=', False)])
        #if any((((line.date_end > self.date_begin and line.date_begin < self.date_begin) or (line.date_end > self.date_end and line.date_begin < self.date_end ) or (line.date_end < self.date_end and line.date_begin > self.date_begin)) and line.id != self.id) and line.product_id.id == self.product_id.id for
        #       line in evento):
        #if 'organizer_id' not in vals:
        #    raise UserError('Infome o Cliente.')
        date_b = self.date_begin
        if 'date_begin' in vals:
            date_b = vals.get('date_begin')
        date_e = self.date_end
        if 'date_end' in vals:
            date_e = vals.get('date_end')
        prod = self.product_id.id
        if 'product_id' in vals:
            prod = self.env['product.product'].browse(vals['product_id']).id
        if self.tem_evento(date_b, date_e, prod, self.id):
            raise UserError('Existe um evento ocorrendo neste horário')
        else:
            vals['qty'] = self.set_duration()
            res = super(EventEvent, self).write(vals)
        return res

    @api.model
    def create(self, vals):
        if 'organizer_id' in vals:
            if vals.get('organizer_id') == False:
                raise UserError('Infome o Cliente.')
        else:
            raise UserError('Infome o Cliente.')
        res = super(EventEvent, self).create(vals)
        date_b = '2001-01-01 11:00:00'
        if 'date_begin' in vals:
            date_b = vals.get('date_begin')
        date_e = '2001-01-01 11:00:00'
        if 'date_end' in vals:
            date_e = vals.get('date_end')
        prod = 1
        if 'product_id' in vals:
            prod = vals.get('product_id')

        if self.tem_evento(date_b, date_e, prod, res.id):
            raise UserError('Existe um evento ocorrendo neste horário')
        #if 'organizer_id' in vals:
        #    reg_ids = {}
        #    reg_ids['partner_id'] = prt_id
        #    reg_ids['event_id'] = res.id
        #    reg_ids['name'] = prt_ids.name
        #    reg_ids['company_id'] = vals.get('address_id')
        #    reg = self.env['event.registration']
        #    reg.create(reg_ids)
        return res

    @api.one
    def button_done(self):
        self.state = 'done'
        venda = self.env['sale.order']
        vals = {}
        vals['partner_id'] = self.organizer_id.id
        vals['company_id'] = self.address_id.company_id.id
        order_line = []

        tz = False
        if self.user_id:
            user = self.env['res.users'].browse(self.user_id.id)
            tz = user.partner_id.tz

        att_tz = timezone(tz or 'utc')

        attendance_dt = datetime.datetime.strptime(self.date_begin, DEFAULT_SERVER_DATETIME_FORMAT)
        att_tz_dt = pytz.utc.localize(attendance_dt)
        att_tz_dt = att_tz_dt.astimezone(att_tz)
        dt_begin = datetime.datetime.strftime(att_tz_dt, DEFAULT_SERVER_DATETIME_FORMAT)
        attendance_dt = datetime.datetime.strptime(self.date_end, DEFAULT_SERVER_DATETIME_FORMAT)
        att_tz_dt = pytz.utc.localize(attendance_dt)
        att_tz_dt = att_tz_dt.astimezone(att_tz)
        dt_end = datetime.datetime.strftime(att_tz_dt, DEFAULT_SERVER_DATETIME_FORMAT)

        servico =  self.product_id.name
        if dt_begin:
            data_s = dt_begin[8:10] + '/' + dt_begin[5:7] + '/' + dt_begin[0:4]
            servico = self.product_id.name + ' (' + data_s
        if dt_begin:
            data_s = dt_begin[11:13] + ':' + dt_begin[14:16]
            servico = servico + ' - ' + data_s
        if dt_end:
            data_s = dt_end[11:13] + ':' + dt_end[14:16]
            servico = servico + ' - ' + data_s + ')'

        order_line.append((0, 0, {
            'product_id': self.product_id.id,
            'name': servico,
             #'price_unit': 1,
            'product_uom_qty': self.qty,
            #'uom_id': self.product_id.uom_id.id
        }))
        vals['order_line'] = order_line
        vnd_ids = venda.create(vals)
        vnd_ids.action_confirm()

    @api.model
    def default_get(self, fields):
        res = super(EventEvent, self).default_get(fields)
        res['organizer_id'] = False
        return res
