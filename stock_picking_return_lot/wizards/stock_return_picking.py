# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, _
from odoo.exceptions import UserError


class ReturnPicking(models.TransientModel):

    _inherit = "stock.return.picking"

    
    def _create_returns(self):
        # import pudb;pu.db
        for return_move in self.product_return_moves.mapped('move_id'):
            return_move.move_dest_ids.filtered(lambda m: m.state not in ('done', 'cancel'))._do_unreserve()

        # create new picking for returned products
        picking_type_id = self.picking_id.picking_type_id.return_picking_type_id.id or self.picking_id.picking_type_id.id
        new_picking = self.picking_id.copy({
            'move_lines': [],
            'picking_type_id': picking_type_id,
            'state': 'draft',
            'origin': _("Return of %s", self.picking_id.name),
            'location_id': self.picking_id.location_dest_id.id,
            'location_dest_id': self.location_id.id})
        new_picking.message_post_with_view('mail.message_origin_link',
            values={'self': new_picking, 'origin': self.picking_id},
            subtype_id=self.env.ref('mail.mt_note').id)
        returned_lines = 0
        for return_line in self.product_return_moves:
            if not return_line.move_id:
                raise UserError(_("You have manually created product lines, please delete them to proceed."))
            # TODO sle: float_is_zero?
            if return_line.quantity:
                returned_lines += 1
                vals = self._prepare_move_default_values(return_line, new_picking)
                r = return_line.move_id.copy(vals)
                vals = {}

                # +--------------------------------------------------------------------------------------------------------+
                # |       picking_pick     <--Move Orig--    picking_pack     --Move Dest-->   picking_ship
                # |              | returned_move_ids              ↑                                  | returned_move_ids
                # |              ↓                                | return_line.move_id              ↓
                # |       return pick(Add as dest)          return toLink                    return ship(Add as orig)
                # +--------------------------------------------------------------------------------------------------------+
                move_orig_to_link = return_line.move_id.move_dest_ids.mapped('returned_move_ids')
                # link to original move
                move_orig_to_link |= return_line.move_id
                # link to siblings of original move, if any
                move_orig_to_link |= return_line.move_id\
                    .mapped('move_dest_ids').filtered(lambda m: m.state not in ('cancel'))\
                    .mapped('move_orig_ids').filtered(lambda m: m.state not in ('cancel'))
                move_dest_to_link = return_line.move_id.move_orig_ids.mapped('returned_move_ids')
                # link to children of originally returned moves, if any. Note that the use of
                # 'return_line.move_id.move_orig_ids.returned_move_ids.move_orig_ids.move_dest_ids'
                # instead of 'return_line.move_id.move_orig_ids.move_dest_ids' prevents linking a
                # return directly to the destination moves of its parents. However, the return of
                # the return will be linked to the destination moves.
                move_dest_to_link |= return_line.move_id.move_orig_ids.mapped('returned_move_ids')\
                    .mapped('move_orig_ids').filtered(lambda m: m.state not in ('cancel'))\
                    .mapped('move_dest_ids').filtered(lambda m: m.state not in ('cancel'))
                vals['move_orig_ids'] = [(4, m.id) for m in move_orig_to_link]
                vals['move_dest_ids'] = [(4, m.id) for m in move_dest_to_link]
                # import pudb;pu.db
                for lines in return_line.move_id.move_line_nosuggest_ids:
                    # lines.lot_id = return_line.move_id.move_line_nosuggest_ids.lot_id.id

                    line = {}
                    line["date"] = fields.Datetime.now()
                    line["reference"] = lines.picking_id.name
                    line["origin"] = lines.picking_id.origin
                    line["product_id"] = lines.picking_id.product_id.id
                    line["location_id"] = lines.location_dest_id.id
                    line["location_dest_id"] = lines.location_id.id
                    line["qty_done"] = lines.qty_done
                    line["lot_id"] = lines.lot_id.id
                    line["company_id"] = lines.company_id.id
                    line["picking_id"] = new_picking.id
                    line["product_uom_id"] = lines.product_uom_id.id
                    stock_line = lines.env['stock.move.line']
                    line_id = stock_line.create(line).id

                    vals["move_line_nosuggest_ids"] = [(6,0,[line_id])]

                r.write(vals)
        if not returned_lines:
            raise UserError(_("Please specify at least one non-zero quantity."))

        # import pudb;pu.db
        new_picking.action_confirm()
        new_picking.action_assign()
        return new_picking.id, picking_type_id


        # result = super(ReturnPicking, self)._create_returns()
        # # return result
        # vals = {}
        # if self.product_return_moves.lot_ids:
        #     vals["product_id"] = self.product_return_moves.product_id.id
        #     vals["product_uom_qty"] = self.product_return_moves.quantity
        #     vals["quantity_done"] = self.product_return_moves.quantity
        #     vals["name"] = self.picking_id.name
        #     vals["product_uom"] = self.picking_id.product_id.uom_id.id
        #     vals["location_id"] = self.original_location_id.id
        #     vals["location_dest_id"] = self.parent_location_id.id
        #     vals["picking_id"] = self.picking_id.id
        #     vals["partner_id"] = self.picking_id.partner_id.id

            
        #     line = {}
        #     line["date"] = fields.Datetime.now()
        #     line["reference"] = self.picking_id.name
        #     line["origin"] = self.picking_id.origin
        #     line["product_id"] = self.picking_id.product_id.id
        #     line["location_id"] = self.original_location_id.id
        #     line["location_dest_id"] = self.parent_location_id.id
        #     line["qty_done"] = self.product_return_moves.quantity
        #     line["lot_id"] = self.product_return_moves.lot_ids.id
        #     line["company_id"] = self.picking_id.company_id.id
        #     line["picking_id"] = self.picking_id.id
        #     line["product_uom_id"] = self.picking_id.product_id.uom_id.id
        #     stock_line = self.env['stock.move.line']
        #     line_id = stock_line.create(line).id

        #     vals["move_line_nosuggest_ids"] = [(6,0,[line_id])]
        #     stock = self.env['stock.move']
        #     stock.create(vals)
        # return result