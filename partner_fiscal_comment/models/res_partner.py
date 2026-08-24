# -*- coding: utf-8 -*-
# © 2018  Carlos R. Silveira
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.addons.l10n_br_fiscal.constants.fiscal import (
    FISCAL_COMMENT_DOCUMENT,
)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    comment_ids = fields.Many2many(
        comodel_name="l10n_br_fiscal.comment",
        domain=[("object", "=", FISCAL_COMMENT_DOCUMENT)],
        string="Comment",
    )