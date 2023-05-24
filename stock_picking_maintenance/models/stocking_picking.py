# -*- encoding: utf-8 -*-

from odoo import models, _

class StockPicking(models.Model): 
    _inherit = "stock.picking"


    def _action_done(self):
        result = super(StockPicking, self)._action_done()
        # TODO criar somente qdo for um tipo especifico de Picking
        for item in self.move_line_nosuggest_ids:
            if item.picking_id.picking_type_id.sequence_code == "IN":
                vals = {}
                vals["name"] = f"{self.name} - {item.lot_id.id} "
                vals["company_id"] = self.company_id.id
                vals["origin"] = self.origin
                vals["lot_id"] = item.lot_id.id
                #["invoice_method"] = self.invoice_method.id
                vals["location_id"] = self.location_id.id
                vals["product_id"] = item.product_id.id
                vals["product_qty"] = item.qty_done
                vals["product_uom"] = item.product_uom_id.id
                    # vals["user_id"] = self.user_id.id
                    # vals["schedule_date"] = self.scheduled_date
                ordem = self.env['repair.order']        
                ordem.create(vals)
        return result
        
