# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp

"""
class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    
    
    def _prepare_invoice(self):
        res = super(PurchaseOrder, self)._prepare_invoice()
        res['document_number'] = self.document_number
        res['document_serie_id'] = self.document_serie_id
        res['document_type_id'] = self.document_type_id
        res['document_key'] = self.document_key
        res['issuer'] = self.issuer
        return res        
"""

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"
    
    num_item_xml = fields.Integer('N.Item')
    product_uom_xml = fields.Many2one('product.uom', string='Un.(xml)')
    product_qty_xml = fields.Float(string='Qtde(xml)', digits=dp.get_precision('Product Unit of Measure'))
