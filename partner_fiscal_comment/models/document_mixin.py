# -*- coding: utf-8 -*-
# © 2018  Carlos R. Silveira
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

class DocumentMixin(models.AbstractModel):
    _inherit = "l10n_br_fiscal.document.mixin"

    @api.depends("fiscal_operation_id", "partner_id")
    def _compute_comment_ids(self):
        for doc in self:
            if doc.fiscal_operation_id:
                doc.comment_ids = doc.fiscal_operation_id.comment_ids
                if doc.partner_id and doc.partner_id.comment_ids:
                    doc.comment_ids |= doc.partner_id.comment_ids
            elif doc.comment_ids is None:
                doc.comment_ids = []