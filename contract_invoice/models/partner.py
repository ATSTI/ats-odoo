# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    payment_mode_id = fields.Many2one(
        'l10n_br.payment.mode',
        string='Payment Mode'
        )
