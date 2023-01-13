# Copyright 2020 ForgeFlow S.L. (https://forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class MaintenanceRequest(models.Model):
    _inherit = "maintenance.request"

    origin = fields.Char(
        string="Origem",
    )    
    
    lot_id = fields.Many2one(
        "stock.production.lot",
        string="lote",
    )

    def action_done(self):
        state = self.env['maintenance.stage'].search([('done', '=', True)],limit=1)
        self.write({'stage_id': state.id})
        # TODO criar e concluir uma devolucao para o estoque
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
        prod['product_id'] = self.equipment_id.product_id.id
        prod['lot_id'] = self.lot_id.id
        prod['qty_done'] = 1.0
        prod['location_id'] = type_operation.default_location_src_id.id
        prod['location_dest_id'] = type_operation.default_location_dest_id.id
        prod['product_uom_id'] = self.equipment_id.product_id.uom_id.id
        line.append((0, 0,prod))
        vals["move_line_ids_without_package"] = line
        pick = self.env["stock.picking"].create(vals)
        pick.button_validate()