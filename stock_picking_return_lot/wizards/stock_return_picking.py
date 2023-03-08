# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ReturnPicking(models.TransientModel):

    _inherit = "stock.return.picking"

    def _create_returns(self):
        import pudb;pu.db
        result = super(ReturnPicking, self)._create_returns()
        vals = {}
        if self.product_return_moves.lot_ids:
            vals["product_id"] = self.product_return_moves.product_id.id
            vals["product_uom_qty"] = self.product_return_moves.quantity
            vals["quantity_done"] = self.product_return_moves.quantity
            
            line = {}
            line["date"] = fields.Datetime.now()
            line["reference"] = self.picking_id.name
            line["origin"] = self.picking_id.origin
            line["product_id"] = self.picking_id.product_id.id
            line["location_id"] = self.original_location_id.id
            line["location_dest_id"] = self.parent_location_id.id
            line["qty_done"] = self.product_return_moves.quantity
            line["lot_id"] = self.product_return_moves.lot_ids.id
            line["company_id"] = self.picking_id.company_id.id
            line["product_uom_id"] = self.picking_id.product_id.uom_id.id
            stock_line = self.env['stock.move.line']
            line_id = stock_line.create(line).id

            vals["move_line_nosuggets_ids"] = [(6,0,[line_id])]
            stock = self.env['stock.move']
            stock.create(vals)
        return result