# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    sale_tag_ids = fields.Many2many(comodel_name="contract.tag", compute="_compute_sale_tag_ids", string="Marcadores (FATURA)")

    @api.depends("sale_tag_ids")
    def _compute_sale_tag_ids(self):
        # hoje = date.today()
        # primeiro_dia_mes_anterior = (hoje.replace(day=1) - relativedelta(months=1))
        # primeiro_dia_mes_anterior = datetime.combine(primeiro_dia_mes_anterior, datetime.min.time())
        for order in self:
            if order.sale_tag_ids:
                return True
            if order.partner_id and order.partner_id.contract_ids:
                order.sale_tag_ids = order.partner_id.contract_ids.mapped("tag_ids")
            else:
                order.sale_tag_ids = False

