# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockReturnPicking(models.TransientModel):

    _inherit = "stock.return.picking.line"

    lot_ids = fields.Many2many(
        comodel_name="stock.production.lot", related="move_id.lot_ids"
    )

    def _create_returns(self):
        result = super(StockReturnPicking, self)._create_returns(vals)
        vals = {}
        if self.lot_ids:
            vals["product_id"] = self.product_id.id
            vals["product_uom_qty"] = self.product_uom_qty.id
            vals["quantity_done"] = self.quantity_done.id
            
            line = {}
            line["date"] = fields.datetime.now()
            line["reference"] = self.pickinkg_id.name
            line["origin"] = self.pickinkg_id.origin
            line["produc_id"] = self.pickinkg_id.product_id
            line["location_id"] = self.original_location_id.id
            line["location_dest_id"] = self.parent_location_id.id
            line["qty_done"] = self.pickinkg_id.product_uom_qty
            line["lot_id"] = self.lot_ids
            stock_line = self.env['stock.move.line']
            line_id = stock_line.create(line).id

            vals["move_line_nosuggets_ids"] = [(6,0,[line_id])]
            stock = self.env['stock.move']
            stock.create(vals)
        return result