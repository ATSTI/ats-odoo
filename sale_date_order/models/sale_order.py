# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _prepare_confirmation_values(self):
        if self.date_order:
            return {
                'state': 'sale'
            }
        else:
            return {
                'state': 'sale',
                'date_order': fields.Datetime.now()
            }
