# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from datetime import date, datetime
from odoo.addons import decimal_precision as dp

class AccountMove(models.Model):
    _inherit = 'account.move'
    

    def _prepare_edoc_vals(self, inv, inv_lines, serie_id):
        res = super(AccountMove, self)._prepare_edoc_vals(inv, inv_lines, serie_id)
        res['data_fatura'] = inv.nfe_data_entrada
        return res


    @api.model
    def create(self, vals):
        invoice = super(AccountMove, self).create(vals)
        purchase = invoice.invoice_line_ids.mapped('purchase_line_id.order_id')
        if purchase and not invoice.refund_invoice_id:
            if purchase:
                invoice.document_number = purchase.document_number
                invoice.document_serie_id = purchase.document_serie_id
                invoice.document_type_id = purchase.document_type_id
                invoice.document_key = purchase.document_key
                invoice.issuer = purchase.issuer
            message = _("This vendor bill has been created from: %s") % (",".join(["<a href=# data-oe-model=purchase.order data-oe-id="+str(order.id)+">"+order.name+"</a>" for order in purchase]))
            invoice.message_post(body=message)
        return invoice
        
    def _prepare_invoice_line_from_po_line(self, line):
        res = super(AccountMove, self)._prepare_invoice_line_from_po_line(
            line)
        res['num_item_xml'] = line.num_item_xml
        res['product_uom_xml'] = line.product_uom_xml.id
        res['product_qty_xml'] = line.product_qty_xml
        return res

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    num_item_xml = fields.Integer('N.Item')
    product_uom_xml = fields.Many2one('product.uom', string='Un.(xml)')
    product_qty_xml = fields.Float(string='Qtde(xml)', digits=dp.get_precision('Product Unit of Measure'))    
