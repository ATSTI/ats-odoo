# -*- coding: utf-8 -*- © 2017 Carlos R. Silveira, ATSti
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re
from odoo import api, fields, models, _


class CrmLead(models.Model):
    _inherit = "crm.lead"


    partner_city = fields.Char(
        string='Cidade do Parceiro',
        readonly=True,
        compute="_compute_city_uf_partner",
        store=True
    )

    partner_uf = fields.Char(
        string='Estado do Parceiro',
        readonly=True,
        compute="_compute_city_uf_partner",
        store=True
    )

    @api.depends('partner_id.city_id', 'partner_id.state_id')
    def _compute_city_uf_partner(self):
        for crm in self:
            if crm.partner_id:
                crm.partner_city = crm.partner_id.city_id.name if crm.partner_id.city_id else ''
                crm.partner_uf = crm.partner_id.state_id.code if crm.partner_id.state_id else ''
            else:
                crm.partner_city = ''
                crm.partner_uf = ''

