# © 2018  Carlos R. Silveira
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from ast import literal_eval
from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError


class RepairOrder(models.Model):
    _inherit = "repair.order"

    # def action_repair_confirm(self):
    #     super(Repair, self).action_repair_confirm(vals)
    #     type_operation = self.env['stock.picking.type'].search([
    #             ('name', '=', 'Manutenção')])
    #     line = []
    #     vals ={
    #         'location_id': type_operation.default_location_src_id.id,
    #         'location_dest_id': type_operation.default_location_dest_id.id,
    #         'picking_type_id': type_operation.id,
    #         'origin': self.name,
    #     }
    #     prod = {}
    #     prod['product_id'] = self.product_id.id
    #     prod['lot_id'] = self.lot_id.id
    #     prod['qty_done'] = 1.0
    #     prod['location_id'] = type_operation.default_location_src_id.id
    #     prod['location_dest_id'] = type_operation.default_location_dest_id.id
    #     prod['product_uom_id'] = self.product_id.uom_id.id
    #     line.append((0, 0,prod))
    #     vals["move_line_ids_without_package"] = line
    #     pick = self.env["stock.picking"].create(vals)
    #     pick.button_validate()
    #     self.message_post(
    #         body=f"Criado movimento de estoque - {pick.name}",
    #         subject=_('Equipamento movido para o estoque!'),
    #         message_type='notification'
    #     )
    #     return True

    def action_repair_done(self):
        """ Creates stock move for operation and stock move for final product of repair order.
        @return: Move ids of final products

        """
        if self.filtered(lambda repair: not repair.repaired):
            raise UserError(_("Repair must be repaired in order to make the product moves."))
        self._check_company()
        self.operations._check_company()
        self.fees_lines._check_company()
        res = {}
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        Move = self.env['stock.move']
        for repair in self:
            # Try to create move with the appropriate owner
            owner_id = False
            available_qty_owner = self.env['stock.quant']._get_available_quantity(repair.product_id, repair.location_id, repair.lot_id, owner_id=repair.partner_id, strict=True)
            if float_compare(available_qty_owner, repair.product_qty, precision_digits=precision) >= 0:
                owner_id = repair.partner_id.id

            moves = self.env['stock.move']
            for operation in repair.operations:
                move = Move.create({
                    'name': repair.name,
                    'product_id': operation.product_id.id,
                    'product_uom_qty': operation.product_uom_qty,
                    'product_uom': operation.product_uom.id,
                    'partner_id': repair.address_id.id,
                    'location_id': operation.location_id.id,
                    'location_dest_id': operation.location_dest_id.id,
                    'repair_id': repair.id,
                    'origin': repair.name,
                    'company_id': repair.company_id.id,
                })

                # Best effort to reserve the product in a (sub)-location where it is available
                product_qty = move.product_uom._compute_quantity(
                    operation.product_uom_qty, move.product_id.uom_id, rounding_method='HALF-UP')
                available_quantity = self.env['stock.quant']._get_available_quantity(
                    move.product_id,
                    move.location_id,
                    lot_id=operation.lot_id,
                    strict=False,
                )
                move._update_reserved_quantity(
                    product_qty,
                    available_quantity,
                    move.location_id,
                    lot_id=operation.lot_id,
                    strict=False,
                )
                # Then, set the quantity done. If the required quantity was not reserved, negative
                # quant is created in operation.location_id.
                move._set_quantity_done(operation.product_uom_qty)

                if operation.lot_id:
                    move.move_line_ids.lot_id = operation.lot_id

                moves |= move
                operation.write({'move_id': move.id, 'state': 'done'})
            type_operation = self.env['stock.picking.type'].search([
                ('name', '=', 'Manutenção')])
            move = Move.create({
                'name': repair.name,
                'product_id': repair.product_id.id,
                'product_uom': repair.product_uom.id or repair.product_id.uom_id.id,
                'product_uom_qty': repair.product_qty,
                'partner_id': repair.address_id.id,
                'location_id': repair.location_id.id,
                'location_dest_id': type_operation.default_location_dest_id.id,
                'move_line_ids': [(0, 0, {'product_id': repair.product_id.id,
                                           'lot_id': repair.lot_id.id,
                                           'product_uom_qty': 0,  # bypass reservation here
                                           'product_uom_id': repair.product_uom.id or repair.product_id.uom_id.id,
                                           'qty_done': repair.product_qty,
                                           'package_id': False,
                                           'result_package_id': False,
                                           'owner_id': owner_id,
                                           'location_id': repair.location_id.id, #TODO: owner stuff
                                           'company_id': repair.company_id.id,
                                           'location_dest_id': type_operation.default_location_dest_id.id,})],
                'repair_id': repair.id,
                'origin': repair.name,
                'company_id': repair.company_id.id,
            })
            consumed_lines = moves.mapped('move_line_ids')
            produced_lines = move.move_line_ids
            moves |= move
            moves._action_done()
            produced_lines.write({'consume_line_ids': [(6, 0, consumed_lines.ids)]})
            res[repair.id] = move.id
        return res