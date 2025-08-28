# -*- coding: utf-8 -*-

from tempfile import template
from odoo import api, fields, models, _


class PurchaseItensLine(models.Model):
    _name = 'purchase.itens.line'

    name = fields.Char(string="Nome")
    product_id = fields.Many2one('product.product', string="Id do Produto")
    product_cst = fields.Float(string="Custo do produto")
    price = fields.Float(string="Preço atual")
    margin = fields.Integer(string="Margem atual")
    new_price = fields.Float(string="Novo preço", default=0.0)
    new_margin = fields.Integer(string="Nova margem(%)", default=0.0)

    @api.onchange('new_margin', 'new_price')
    def onchange_new_margin(self):
        if self.new_margin > 0 and self.new_price == 0:
            self.new_price = self.product_cst * (1 + (float(self.new_margin) / 100))

    @api.onchange('new_price', 'new_margin')
    def onchage_new_price(self):
        if self.new_price > 0 and self.new_margin == 0:
            self.new_margin = ((self.new_price * 100) / self.product_cst) - 100


class PurchaseItens(models.Model):
    _name = "purchase.itens"

    purchase_order_ref = fields.Char(string="Compra")
    purchase_lines = fields.Many2many('purchase.itens.line',)
    state = fields.Selection([
        ('new','Novo'),
        ('done', 'Feito'),
        ],
        string='Status',
        readonly=True,
        index=True,
        copy=False,
        default='new',
        track_visibility='onchange')

    def save_product_changes(self):
        for l in self.purchase_lines:
            product = self.env['product.template'].browse(l.product_id.product_tmpl_id.id)
            if l.new_price > 0:
                product.write({
                    'list_price': l.new_price,
                    'standard_price': l.product_cst,
                })
                if product.shopee:
                    product.calcula_valor_venda_shopee()
                if product.meli:
                    product.calcula_valor_venda_meli()
                if product.used_in_bom_count:
                    bom = self.env['mrp.bom'].search(
                        [('bom_line_ids.product_tmpl_id', '=', product.id)])
                    for p in bom:
                        p.product_tmpl_id.button_bom_cost()
                        if p.shopee:
                            p.calcula_valor_venda_shopee()
                        if p.meli:
                            p.calcula_valor_venda_meli()
            if l.new_margin > 0:
                product.margin = l.new_margin
        self.state = 'done'
