# -*- coding: utf-8 -*-
###################################################################################
#
#    ATS TI Soluções.
#
###################################################################################

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    tag_campo = fields.Many2many('res.partner.category', string='Marcadores', compute='_compute_category', store=True,)

    @api.depends('partner_id')
    def _compute_category(self):
        for inv in self:
            if inv.partner_id and inv.partner_id.category_id:
                inv.tag_campo = inv.partner_id.category_id