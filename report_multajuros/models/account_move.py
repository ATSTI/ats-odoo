from odoo import models, fields, api



class AccountMove(models.Model):
    _inherit = "account.move"

    evento = fields.Char(string='Evento')