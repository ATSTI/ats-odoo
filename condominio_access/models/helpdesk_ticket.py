from odoo import fields, models

class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    residence_id = fields.Many2one(
        "condo.residence",
        string="Residência",
    )