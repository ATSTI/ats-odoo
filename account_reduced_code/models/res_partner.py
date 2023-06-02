# -*- coding: utf-8 -*-
# © 2018  Carlos R. Silveira
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    code_reduced = fields.Char(size=64, string="Cód. Reduzido")
