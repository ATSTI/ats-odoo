# -*- coding: utf-8 -*- © 2017 Carlos R. Silveira, ATSti
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _

class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    intermediador = fields.Many2one('res.partner',string="Agente intermediador")

    @api.depends('partner_id')
    def onchange_partner_id(self):
        result = super().onchange_partner_id()
        if self.partner_id:
            if self.partner_id.agente_int:
                self.intermediador = self.partner_id.agente_int
        return result