# -*- coding: utf-8 -*-

from odoo import fields, models, _, api
from odoo.exceptions import UserError
from datetime import datetime, timedelta

class FSMOrder(models.Model):
    _inherit = "fsm.order"

    @api.onchange('person_id')
    def _onchange_person_id(self):
        if self.person_id:
            self.write({'person_ids': [(4, self.person_id.id)]})
            users = self.env['hr.employee']
            us = users.search([('name', '=', self.person_id.name)])
            if us:
                vals_line = {
                    'employee_id': us.id,
                    'product_id': 39,
                }
                self.write({'employee_timesheet_ids': [(0, 0, vals_line)]})
            else:
                new_us = users.create({
                    'name': self.person_id.name,
                    'work_email': self.person_id.email,
                    'resource_calendar_id': self.person_id.calendar_id.id,
                    'work_location': self.person_id.location_ids.location_id.name,
                    'work_phone': self.person_id.phone,
                })
                vals_line = {
                    'employee_id': new_us.id,
                    'product_id': 39,
                }
                self.write({'employee_timesheet_ids': [(0, 0, vals_line)]})
            if self.employee_timesheet_ids:
                for line in self.employee_timesheet_ids:
                    line.name = f'{line.product_id.name}'          

    def write(self, vals):
        res = super(FSMOrder, self).write(vals)
        if self.person_id.name not in self.name:
            name = ''
            for person in self.person_ids:
                if name == '':
                    name = f'{person.name} -'
                else:
                    name = f'{name} {person.name} -'
            self.name = f'{name} {self.name}'
        else:
            return res

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for va in vals_list:
            if_exists = self.env["fsm.order"].search([
                ('id', '!=', res.id),
                ('scheduled_date_start', '<=', res.scheduled_date_end),
                ('scheduled_date_end', '>=', res.scheduled_date_start),
            ])
            for ex in if_exists:
                for person in ex.person_ids:
                    for person2 in res.person_ids:
                        if person.id == person2.id:
                            raise UserError(_("Horário indisponível, já existe um evento agendado para este horário."))
        if res.person_id:
            name = ''
            for person in res.person_ids:
                if name == '':
                    name = f'{person.name} -'
                else:
                    name = f'{name} {person.name} -'
            res.name = f'{name} {res.name}'
        res._create_calendar_event()
        return res