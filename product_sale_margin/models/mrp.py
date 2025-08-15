# -*- encoding: utf-8 -*-

from odoo import fields,models,api, _
from odoo.exceptions import UserError

class MrpProduction(models.Model):
    _inherit = 'mrp.production'
    
    def button_mark_done(self):
        res = super(MrpProduction, self).button_mark_done()
        prod = self.product_id.product_tmpl_id
        prod.button_bom_cost()
        if prod.margin:
            prod.list_price = prod.standard_price * (1 + (float(prod.margin)/100))
        return res