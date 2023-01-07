# -*- coding: utf-8 -*-

from odoo import models,fields

class InvoiceEletronic(models.Model):
    _inherit = 'invoice.eletronic'


    cod_mun_env = fields.Char(string='Cód. Mun. de envio ')
    cod_mun_ini = fields.Char(string='Cód. Mun. iníc. prestação')
    cod_mun_fim = fields.Char(string='Cód. Mun. térm. prestação')
    tp_emiss_cte = fields.Char(string='Tipo Emissao Cte')
    
    model = fields.Selection(selection_add=[
        ('57', u'57-CTe'),
        ('67', u'67-CTe-OS'),
        ])
