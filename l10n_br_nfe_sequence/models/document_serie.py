# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, api, fields, models

from odoo.addons.l10n_br_fiscal.constants.fiscal import (
    DOCUMENT_ISSUER_COMPANY,
)


class DocumentSerie(models.Model):
    _inherit = "l10n_br_fiscal.document.serie"

    def next_seq_number(self):
        self.ensure_one()
        document = self.env["l10n_br_fiscal.document"].search([
            ("document_number", "!=", False),
            ("document_serie_id", "=", self.id),
            ("document_type_id", "=", self.document_type_id.id),
            ("issuer", "=", DOCUMENT_ISSUER_COMPANY),
            ("company_id", "=", self.company_id.id),
            ], order="document_number desc", limit=1
        )
        if document:
            try:
                document_number = int(document.document_number) + 1
            except:
                document_number = self.internal_sequence_id._next()    
        else:
            document_number = self.internal_sequence_id._next()
        if self._is_invalid_number(document_number) or self.check_number_in_use(
            document_number
        ):
            document_number = self.next_seq_number()
        return document_number
