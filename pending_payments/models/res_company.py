from odoo import models, fields, api

class Company(models.Model):
    _inherit = 'res.company'

    days_to_notify = fields.Integer(
        string="Dias para notificar sobre pendências",
        default=5,
    )
    notify = fields.Boolean(
        string="Notificar sobre algo?",
        default=False,
    )
    notify_customers = fields.Text(
        string="Notificação para clientes",
    )