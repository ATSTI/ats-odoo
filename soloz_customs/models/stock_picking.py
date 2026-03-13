from odoo import api, fields, models, _
from odoo.exceptions import UserError

class StockPicking(models.Model):

    _inherit = 'stock.picking'

    def action_confirm(self):
        for res in self:
            if res.move_ids and not res.move_ids.purchase_line_id:
                po = self.env['purchase.order'].search([('name', '=', res.origin)], limit=1)
                if po:
                    products = self.env['purchase.order.line'].search([('order_id', '=', po.id)]).mapped('product_id')
                    for line in res.move_ids_without_package:
                        if line.product_id in products:
                            res.move_ids.purchase_line_id = self.env['purchase.order.line'].search([('order_id', '=', po.id), ('product_id', '=', line.product_id.id)], limit=1).id       
        return super(StockPicking, self).action_confirm()

