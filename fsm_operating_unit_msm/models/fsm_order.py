from odoo import models

class FSMOrder(models.Model):
    _inherit = "fsm.order"

    def account_prepare_invoice(self):
        vals = super().account_prepare_invoice()

        if self.operating_unit_id:
            vals["operating_unit_id"] = self.operating_unit_id.id

        return vals