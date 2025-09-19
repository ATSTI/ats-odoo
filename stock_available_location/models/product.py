# -*- encoding: utf-8 -*-

from odoo import models, _
from odoo.osv import expression


class Product(models.Model):
    _inherit = "product.product"


    def _get_domain_locations(self):
        res = super()._get_domain_locations()

        location_param = self.env["ir.config_parameter"].sudo().get_param("stock.available_location")
        if location_param:
            location_ids = {int(location_param)}
            return self._get_domain_locations_new(location_ids, compute_child=self.env.context.get("compute_child", True))

        return res
