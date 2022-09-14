# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"


    def _prepare_invoice(self):
        self.ensure_one()
        result = super()._prepare_invoice()
        result.update(self._prepare_br_fiscal_dict())

        if self.partner_id and self.partner_id.parent_id:
            result["partner_id"] = self.partner_id.parent_id.id
            result["ref"] = self.partner_id.name

        return result