import re
from odoo import api, fields, models, _
from odoo.exceptions import UserError,ValidationError


class SaleOrder(models.Model):
    _inherit='sale.order'

    def action_confirm(self):
        result = super().action_confirm()
        for order in self:
            order.picking_ids.filtered(
                lambda p: p.state not in ('done', 'cancel')
            ).write({'state': 'draft'})
            
        return result