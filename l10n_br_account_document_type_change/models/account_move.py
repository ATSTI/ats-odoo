# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, models, api

from odoo.addons.l10n_br_fiscal.constants.fiscal import (
    DOCUMENT_ISSUER_COMPANY,
)


class AccountMove(models.Model):
    _inherit = "account.move"
   
    @api.onchange("document_type_id")
    def _onchange_document_type_id(self):
        for doc in self.fiscal_document_ids:
            if (
                doc.document_serie_id
                and doc.document_type_id
                and doc.issuer == DOCUMENT_ISSUER_COMPANY
                and doc.document_number
            ):            
                doc.document_number = False
                doc.document_serie_id = False
                doc._compute_document_serie_id()
