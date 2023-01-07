# -*- coding: utf-8 -*-
###################################################################################
#
#    ATS TI Soluções.
#
###################################################################################

from odoo import api, fields, models, _


class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"
  
    @api.one
    @api.depends('categ_id', 'product_tmpl_id', 'product_id', 'compute_price', 'fixed_price', \
        'pricelist_id', 'percent_price', 'price_discount', 'price_surcharge')
    def _get_pricelist_item_name_price(self):
        if self.categ_id:
            self.name = _("Category: %s") % (self.categ_id.name)
        elif self.product_tmpl_id:
            self.name = '[%s] - %s' %(self.product_tmpl_id.default_code, self.product_tmpl_id.name)
        elif self.product_id:
            self.name = self.product_id.display_name #.replace('[%s]' % self.product_id.code, '')
        else:
            self.name = _("All Products")

        if self.compute_price == 'fixed':
            self.price = ("%s %s") % (self.fixed_price, self.pricelist_id.currency_id.name)
        elif self.compute_price == 'percentage':
            self.price = _("%s %% discount") % (self.percent_price)
        else:
            self.price = _("%s %% discount and %s surcharge") % (self.price_discount, self.price_surcharge)