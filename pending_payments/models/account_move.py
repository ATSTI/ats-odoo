from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    free_access = fields.Boolean(
        string="Liberar Acesso",
        default=False,
    )