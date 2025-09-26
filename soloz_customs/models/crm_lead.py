# -*- coding: utf-8 -*- © 2017 Carlos R. Silveira, ATSti
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re
from odoo import api, fields, models, _


class CrmLead(models.Model):
    _inherit = "crm.lead"


    partner_city = fields.Char(
        string='Cidade do Parceiro',
        readonly=True,
        compute="_compute_city_uf_partner"
    )

    partner_uf = fields.Char(
        string='Estado do Parceiro',
        readonly=True,
        compute="_compute_city_uf_partner"
    )

    @api.depends('partner_id')
    def _compute_city_uf_partner(self):
        for order in self:
            if order.partner_id:
                order.partner_city = order.partner_id.city_id.name
                order.partner_uf = order.partner_id.state_id.code
