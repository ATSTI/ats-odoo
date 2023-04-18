# -*- coding: utf-8 -*-

from odoo import fields, models, _, api

class ChairControl(models.Model):
    _name = 'chair.control'
    _description = "Controle de cadeiras"

    name = fields.Char(string="N. da Cadeira")
    active = fields.Boolean(string='Ativo',default=True)


