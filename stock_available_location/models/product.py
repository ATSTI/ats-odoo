# -*- encoding: utf-8 -*-

from odoo import models, _
from odoo.osv import expression


class Product(models.Model):
    _inherit = "product.product"


    def _get_domain_locations(self):
        '''
        Parses the context and returns a list of location_ids based on it.
        It will return all stock locations when no parameters are given
        Possible parameters are shop, warehouse, location, compute_child
        '''
        Warehouse = self.env['stock.warehouse']

        def _search_ids(model, values):
            ids = set()
            domain = []
            for item in values:
                if isinstance(item, int):
                    ids.add(item)
                else:
                    domain = expression.OR([[(self.env[model]._rec_name, 'ilike', item)], domain])
            if domain:
                ids |= set(self.env[model].search(domain).ids)
            return ids

        # We may receive a location or warehouse from the context, either by explicit
        # python code or by the use of dummy fields in the search view.
        # Normalize them into a list.
        location = self.env.context.get('location')
        if location and not isinstance(location, list):
            location = [location]
        warehouse = self.env.context.get('warehouse')
        if warehouse and not isinstance(warehouse, list):
            warehouse = [warehouse]
        # filter by location and/or warehouse
        if warehouse:
            w_ids = set(Warehouse.browse(_search_ids('stock.warehouse', warehouse)).mapped('view_location_id').ids)
            if location:
                l_ids = _search_ids('stock.location', location)
                location_ids = w_ids & l_ids
            else:
                location_ids = w_ids
        else:
            if location:
                location_ids = _search_ids('stock.location', location)
            else:
                location_ids = set(Warehouse.search([]).mapped('view_location_id').ids)
        #import pudb;pu.db
        location_param = self.env["ir.config_parameter"].sudo().get_param("stock.available_location")
        if location_param:
           location_ids = {int(location_param)}

        return self._get_domain_locations_new(location_ids, compute_child=self.env.context.get('compute_child', True))