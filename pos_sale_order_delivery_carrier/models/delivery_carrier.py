from odoo import fields, models


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    available_in_pos = fields.Boolean(
        string="Available in POS",
        help="Check if you want this shipping method to appear in the Point of Sale",
        default=True,
    )
