from odoo import api, fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    @api.model
    def _domain_delivery_carrier_ids(self):
        return (
            "[('available_in_pos', '=', True),"
            "'|',"
            "('company_id', '=', False),('company_id', '=', company_id)]"
        )

    allow_delivery_carrier = fields.Boolean(default=True)
    delivery_carrier_ids = fields.Many2many(
        comodel_name="delivery.carrier",
        relation="delivery_carrier_pos_config_rel",
        column1="pos_config_id",
        column2="delivery_carrier_id",
        string="Shipping Methods",
        domain=lambda self: self._domain_delivery_carrier_ids(),
    )
