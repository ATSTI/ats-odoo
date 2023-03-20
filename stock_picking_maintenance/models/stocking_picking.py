# -*- encoding: utf-8 -*-

from odoo import models, _

class StockPicking(models.Model): 
    _inherit = "stock.picking"


    def _action_done(self):
        result = super(StockPicking, self)._action_done()
        # TODO criar somente qdo for um tipo especifico de Picking
        for item in self.move_line_ids_without_package:
            if item.picking_id.picking_type_id.sequence_code == "IN":
                vals = {}
                equip_id = self.env['maintenance.equipment'].search([('product_id', '=', item.product_id.id)], limit=1)
                if equip_id:
                    vals["name"] = f"{self.name} - {item.lot_id.id} "
                    vals["equipment_id"] = equip_id.id
                    vals["lot_id"] = item.lot_id.id
                    vals["maintenance_type"] = "preventive" 
                    # vals["user_id"] = self.user_id.id
                    # vals["schedule_date"] = self.scheduled_date
                    ordem = self.env['maintenance.request']        
                    ordem.create(vals)
        return result
        
