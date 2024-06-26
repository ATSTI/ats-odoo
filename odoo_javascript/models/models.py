# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools


class js(models.Model):
    _name='js'
    
    name= fields.Char('Name')
    company_id = fields.Many2one('res.company', 'Empresas')

    @api.model
    def function_name(self):
        import pudb;pu.db
        data = {'teste': 'avcde'}
        return data

    def get_sale_order(self):
        return "TEST"