# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, fields, models

class ResPartner(models.Model):

    _inherit = 'res.partner'

    @api.model
    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        self.env["hr.employee"].create({
            "name": vals.get("name"),
            "address_id": res.id,
            "image_1920": vals.get("image_1920"),
        })
        return res    
    
    def write(self, vals):
        result = super(ResPartner, self).write(vals)
        if vals.get("image_1920"):
            hr = self.env["hr.employee"].search([("address_id", "=", self.id)])
            if hr:
                hr.write({"image_1920": vals.get("image_1920")})
        return result