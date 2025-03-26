# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.onchange("product_uom_id")
    def _onchange_product_uom_id(self):
        if self.product_uom_id:
            self.uot_id = self.product_uom_id.id
    