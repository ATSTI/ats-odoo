from odoo import models, fields


class CondoRecurringVisitor(models.Model):
    _name = "condo.recurring.visitor"
    _description = "Visitantes Recorrentes"

    residence_id = fields.Many2one(
        "condo.residence",
        string="Residência",
        ondelete="cascade"
    )

    morador_id = fields.Many2one(
        "res.partner",
        string="Morador",
        required=True,
        domain="[('is_morador','=',True)]"
    )

    partner_id = fields.Many2one(
        "res.partner",
        string="Visitante",
        required=True
    )

    expediente = fields.Char(
        string="Expediente"
    )