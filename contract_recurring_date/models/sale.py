# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime, timedelta
from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    sale_tag_ids = fields.Many2many(comodel_name="contract.tag", string="Marcadores (FATURA)")
