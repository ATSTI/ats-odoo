# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, _
from odoo.exceptions import UserError


class ReturnPicking(models.TransientModel):

    _inherit = "stock.return.picking"

    
    def _create_returns(self):
        new_picking_id, picking_type_id = super(StockReturnPicking, self)._create_returns()
        new_picking = self.env['stock.picking'].browse(new_picking_id)

        for return_line in self.product_return_moves:
            if not return_line.move_id or not return_line.quantity:
                continue

            lote_ids = []
            for move_line in return_line.move_id.move_line_nosuggest_ids:
                line_vals = {
                    "date": fields.Datetime.now(),
                    "reference": move_line.picking_id.name,
                    "origin": move_line.picking_id.origin,
                    "product_id": move_line.product_id.id,
                    "location_id": self.picking_id.location_dest_id.id,
                    "location_dest_id": self.location_id.id,
                    "qty_done": move_line.qty_done,
                    "lot_id": move_line.lot_id.id,
                    "company_id": move_line.company_id.id,
                    "picking_id": new_picking.id,
                    "product_uom_id": move_line.product_uom_id.id,
                    "move_id": return_line.move_id.id,  # vincula ao movimento
                }
                if move_line.lot_id:
                    stock_line = self.env['stock.move.line'].create(line_vals)
                    lote_ids.append(stock_line.id)

            # Se criou move_lines, linka ao movimento de retorno
            if lote_ids:
                return_line.move_id.write({
                    "move_line_nosuggest_ids": [(6, 0, lote_ids)]
                })

        return new_picking.id, picking_type_id