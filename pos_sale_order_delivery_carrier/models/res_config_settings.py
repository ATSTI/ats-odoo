from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    pos_allow_delivery_carrier = fields.Boolean(
        related="pos_config_id.allow_delivery_carrier",
        readonly=False,
    )
    pos_delivery_carrier_ids = fields.Many2many(
        related="pos_config_id.delivery_carrier_ids",
        comodel_name="delivery.carrier",
        readonly=False,
    )
