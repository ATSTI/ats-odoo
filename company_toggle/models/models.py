# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools


class js(models.Model):
    _name='js'
    
    name= fields.Char('Name')
    company_id = fields.Many2one('res.company', 'Empresas')


    def send_reminder_preview(self):
        return