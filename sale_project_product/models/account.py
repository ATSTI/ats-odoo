# -*- coding: utf-8 -*-

from odoo import fields, models, _, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    libera = fields.Boolean(string="Entrega Liberada pelo financeiro")
 