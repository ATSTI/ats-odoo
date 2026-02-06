from odoo import _, models, api


from odoo.addons.l10n_br_fiscal.constants.fiscal import (
    DOCUMENT_ISSUER_COMPANY,
)

class Document(models.Model):
    _inherit = "l10n_br_fiscal.document"

    @api.depends("document_type_id", "issuer")
    def _compute_document_serie_id(self):
        for doc in self:
            if (
                not doc.document_serie_id
                and doc.document_type_id
                and doc.issuer == DOCUMENT_ISSUER_COMPANY
            ):
                doc.document_serie_id = doc.document_type_id.get_document_serie(
                    doc.company_id, doc.fiscal_operation_id
                )
            elif doc.document_serie_id is None:
                doc.document_serie_id = False
            elif (
                doc.document_serie_id
                and doc.document_type_id
                and doc.issuer == DOCUMENT_ISSUER_COMPANY
            ):
                doc.document_serie_id = doc.document_type_id.get_document_serie(
                    doc.company_id, doc.fiscal_operation_id
                )
