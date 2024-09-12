
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError

class Company(models.Model):
    _inherit = "res.company"
    _description = 'Companies'

    token_chat = fields.Char("Token do Chat")