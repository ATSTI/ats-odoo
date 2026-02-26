from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = "sale.order"

    partner_city = fields.Char(
        string="Cidade",
        related="partner_id.city",
        store=True,
        readonly=True,
    )

    partner_state_id = fields.Many2one(
        "res.country.state",
        string="Estado",
        related="partner_id.state_id",
        store=True,
        readonly=True,
    )