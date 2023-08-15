# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, api, fields, models

from odoo.addons.l10n_br_fiscal.constants.fiscal import (
    DOCUMENT_ISSUER_COMPANY,
)


class DocumentSerie(models.Model):
    _inherit = "l10n_br_fiscal.document.serie"

    def next_last_number(self):
        document_number = self.internal_sequence_id._next()
        if self._is_invalid_number(document_number) or self.check_number_in_use(
            document_number
        ):
            document_number = self.next_last_number()
        return document_number

    def next_seq_number(self):
        self.ensure_one()
        query = """
            SELECT CAST(document_number AS INTEGER) AS nf
            FROM l10n_br_fiscal_document
            WHERE document_serie_id = %s
            AND document_type_id = %s
            AND company_id = %s
            AND issuer = '%s'
            AND document_number IS NOT NULL
            ORDER BY CAST(document_number AS INTEGER) DESC
            LIMIT 1
        """ % (
                self.id,
                self.document_type_id.id,
                self.company_id.id,
                DOCUMENT_ISSUER_COMPANY
            )
        self._cr.execute(query)
        sql_num = self._cr.fetchall()
        if sql_num:
            for num in sql_num:
                document_number = int(num[0]) + 1
        else:
            document_number = self.internal_sequence_id._next()
        if self._is_invalid_number(document_number) or self.check_number_in_use(
            document_number
        ):
            document_number = self.next_last_number()
        return document_number
