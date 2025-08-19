# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime, timedelta
from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    sale_tag_ids = fields.Many2many(comodel_name="contract.tag", compute="_compute_sale_tag_ids", string="Marcadores (FATURA)")

    @api.depends("sale_tag_ids")
    def _compute_sale_tag_ids(self):
        for order in self:
            order.sale_tag_ids = order.partner_id.contract_ids.tag_ids
