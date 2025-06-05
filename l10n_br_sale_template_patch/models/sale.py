# -*- coding: utf-8 -*-

from odoo import fields, models, _, api

class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    @api.onchange('sale_order_template_id')
    def onchange_sale_order_template_id(self):
        ret = super(SaleOrder, self).onchange_sale_order_template_id()
        if self.sale_order_template_id:
            self.onchange_partner_id()
            for line in self.order_line:
                line._onchange_product_id_fiscal()