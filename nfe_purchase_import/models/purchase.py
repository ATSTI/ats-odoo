# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    
    nfe_num = fields.Integer('Num. NFe')
    nfe_serie = fields.Char('Série')
    nfe_modelo = fields.Char('Modelo')
    nfe_chave =  fields.Char('Chave NFe')
    nfe_emissao = fields.Date('Data Emissão NFe')
    
    @api.multi
    def _prepare_invoice(self):
        res = super(PurchaseOrder, self)._prepare_invoice()
        res['nfe_num'] = self.nfe_num
        res['nfe_serie'] = self.nfe_serie
        res['nfe_modelo'] = self.nfe_modelo
        res['nfe_chave'] = self.nfe_chave
        res['nfe_emissao'] = self.nfe_emissao
        return res        


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"
    
    num_item_xml = fields.Integer('N.Item')
    product_uom_xml = fields.Many2one('product.uom', string='Un.(xml)')
    product_qty_xml = fields.Float(string='Qtde(xml)', digits=dp.get_precision('Product Unit of Measure'))
