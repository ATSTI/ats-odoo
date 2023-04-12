# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import tools
from odoo import api, fields, models


class ListPriceReport(models.Model):
    _name = "list.price.report"
    _description = "Lista de Precos"
    _auto = False
    _rec_name = 'codigo'
    _order = 'codigo'

    name = fields.Char('Produto', readonly=True)
    codigo = fields.Char('Codigo', readonly=True)
    product_id = fields.Many2one('product.product', 'Product', readonly=True)
    categoria = fields.Char('Categoria', readonly=True)
    preco2 = fields.Float('Lista 1', readonly=True)
    preco3 = fields.Float('Lista 2', readonly=True)
    preco1 = fields.Float('Lista 3', readonly=True)
    lista1 = fields.Char('Nome Lista 1', readonly=True)
    lista2 = fields.Char('Nome Lista 2', readonly=True)
    lista3 = fields.Char('Nome Lista 3', readonly=True)

    @api.model_cr
    def init(self):
        self._table = "list_price_report"
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW list_price_report as (
            select pt.id, pt.name, p.default_code as codigo, p.id as product_id
            ,pc.name as categoria, list_price as preco1
            ,list_price-(list_price*((select pl.percent_price
            from product_pricelist_item pl where pl.product_tmpl_id = pt.id
            and pl.pricelist_id = 2)/100)) as preco2
            ,list_price-(list_price*((select pl.percent_price
            from product_pricelist_item pl
            where pl.product_tmpl_id = pt.id
            and pl.pricelist_id = 3)/100)) as preco3
            ,(select ppl.name from product_pricelist ppl where ppl.id = 1) as lista1
            ,(select ppl.name from product_pricelist ppl where ppl.id = 2) as lista2
            ,(select ppl.name from product_pricelist ppl where ppl.id = 3) as lista3
            from product_product p, product_template pt, product_category pc
            where pt.id = p.product_tmpl_id
              and pc.id = pt.categ_id
            )"""
        )
