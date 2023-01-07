# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from datetime import date, datetime
from odoo.addons import decimal_precision as dp

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    nfe_num = fields.Integer('Num. NFe')
    nfe_serie = fields.Char('Série')
    nfe_modelo = fields.Char('Modelo')
    nfe_chave =  fields.Char('Chave NFe')
    nfe_emissao = fields.Date('Data Emissão NFe')
    nfe_data_entrada = fields.Date('Data Entrada')

    def _prepare_edoc_vals(self, inv, inv_lines, serie_id):
        res = super(AccountInvoice, self)._prepare_edoc_vals(inv, inv_lines, serie_id)
        res['data_fatura'] = inv.nfe_data_entrada
        return res


    @api.model
    def create(self, vals):
        invoice = super(AccountInvoice, self).create(vals)
        purchase = invoice.invoice_line_ids.mapped('purchase_line_id.order_id')
        if purchase and not invoice.refund_invoice_id:
            if purchase:
                invoice.nfe_num = purchase.nfe_num
                invoice.nfe_serie = purchase.nfe_serie
                invoice.nfe_modelo = purchase.nfe_modelo
                invoice.nfe_chave = purchase.nfe_chave
                invoice.nfe_emissao = purchase.nfe_emissao
            message = _("This vendor bill has been created from: %s") % (",".join(["<a href=# data-oe-model=purchase.order data-oe-id="+str(order.id)+">"+order.name+"</a>" for order in purchase]))
            invoice.message_post(body=message)
        return invoice
        
    def _prepare_invoice_line_from_po_line(self, line):
        res = super(AccountInvoice, self)._prepare_invoice_line_from_po_line(
            line)
        res['num_item_xml'] = line.num_item_xml
        res['product_uom_xml'] = line.product_uom_xml.id
        res['product_qty_xml'] = line.product_qty_xml
        return res

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    
    num_item_xml = fields.Integer('N.Item')
    product_uom_xml = fields.Many2one('product.uom', string='Un.(xml)')
    product_qty_xml = fields.Float(string='Qtde(xml)', digits=dp.get_precision('Product Unit of Measure'))    
