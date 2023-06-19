# © 2018  Carlos R. Silveira
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from ast import literal_eval
from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError


class Repair(models.Model):
    _inherit = 'repair.order'

    def action_repair_confirm(self):
        super(Repair, self).action_repair_confirm(vals)
        type_operation = self.env['stock.picking.type'].search([
                ('name', '=', 'Manutenção')])
        line = []
        vals ={
            'location_id': type_operation.default_location_src_id.id,
            'location_dest_id': type_operation.default_location_dest_id.id,
            'picking_type_id': type_operation.id,
            'origin': self.name,
        }
        prod = {}
        prod['product_id'] = self.product_id.id
        prod['lot_id'] = self.lot_id.id
        prod['qty_done'] = 1.0
        prod['location_id'] = type_operation.default_location_src_id.id
        prod['location_dest_id'] = type_operation.default_location_dest_id.id
        prod['product_uom_id'] = self.product_id.uom_id.id
        line.append((0, 0,prod))
        vals["move_line_ids_without_package"] = line
        pick = self.env["stock.picking"].create(vals)
        pick.button_validate()
        self.message_post(
            body=f"Criado movimento de estoque - {pick.name}",
            subject=_('Equipamento movido para o estoque!'),
            message_type='notification'
        )
        return True

