# -*- coding: utf-8 -*-

import pytz

from odoo import _, api, fields, models

class CadeiraParticipante(models.Model):
    _name = "cadeira.participante"

    #name = fields.Many2one('chair.control',string="Número da cadeira")
    name = fields.Char(string="Número da cadeira")
    event_id = fields.Many2one('event.event', required=True, ondelete='cascade', index=True, copy=False)
    participant_id = fields.Many2one('event.registration')

    _sql_constraints = [
        ('cadeira_participante_participant_id_uniq', 'unique (participant_id, event_id)',
         u'Essa pessoa já está em uma cadeira!')
    ]


class EventEvent(models.Model):
    _inherit = 'event.event'

    chair_id = fields.Many2many(
        'cadeira.participante', string='Cadeiras disponíveis para o evento')
    criado_cadeiras = fields.Boolean(string='',readonly=True,default=False)

    def write(self, vals):
        res = super(EventEvent,self).write(vals)
        for ch in self.chair_id:
            if not ch.event_id:
                ch.event_id = self.id
        return res


    @api.model
    def create(self, vals):
        event_id = super(EventEvent, self).create(vals)
        cadeira_qty = 60
        #18/06/2018 #####
        #cadeiras = self.env['chair.control'].search([('active','=','True')])
        #colocar aqui a rotina para limitar
        if self.criado_cadeiras:
            return event_id
        val = []
        for i in range(cadeira_qty):
            val.append((0, None, {
                'event_id': event_id.id,
                'name': i + 1,
                }))
        if val:
            event_id['chair_id'] = val
            
        return event_id


    def button_criar_cadeiras(self):
        self.criado_cadeiras = True
        val = {}
        val['event_id'] = self.id
        for i in range(60):
            val['name'] = i + 1
            self.env['cadeira.participante'].create(val)

class EventRegistration(models.Model):
    _inherit = 'event.registration'

    chair = fields.Char(string="Cadeira")

    chair_id = fields.Many2one('cadeira.participante', string="Cadeira",
        domain="[('participant_id', '=', False), \
        ('event_id','=',event_id)]")

    @api.model
    def create(self, vals):
        er_id = super(EventRegistration, self).create(vals)
        if 'chair_id' in vals:
            chair = self.env['cadeira.participante'].search([
                ('name','=',er_id.chair_id.name),
                ('event_id', '=', er_id.event_id.id)
                ], limit=1)
            if chair:
                chair.participant_id = er_id.id
        return er_id        
        

    def write(self, vals):
        res = super(EventRegistration,self).write(vals)
        if 'chair_id' in vals:
            chair = self.env['cadeira.participante'].search([
                ('name','=',self.chair_id.name),
                ('event_id', '=', self.event_id.id)
                ], limit=1)
            if chair:
                chair.participant_id = self.id
            #val = []
            #val.append((0, None, {
            #    'event_id': self.event_id.id,
            #    'participant_id': self.partner_id.id,
            #    'name': self.chair_id.name,
            #    }))
            #self.event_id.write({'chair_id': val})
        return res    

    def button_reg_close(self):
        today = fields.Datetime.now()
        return self.write({'state': 'done', 'date_closed': today})

