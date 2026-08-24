from odoo import models, api
from odoo.addons.l10n_br_fiscal.models.document_mixin import FiscalDocumentMixin
from odoo.addons.l10n_br_fiscal.constants.fiscal import (
    DOCUMENT_ISSUER_COMPANY,
)

class AccountMove(models.Model):
    _inherit = "account.move"

    @api.onchange("document_type_id")
    def _onchange_document_type_id(self):
        for rec in self:
            if not rec.document_type_id:
                continue

            #serie = self.env["l10n_br_fiscal.document.serie"].search([
            #    ("document_type_id", "=", rec.document_type_id.id),
            #    ("active", "=", True),
            #], limit=1)
            if rec.document_serie_id and rec.document_number and rec.issuer == DOCUMENT_ISSUER_COMPANY:
                rec.document_serie_id = False
                rec.document_number = False
                res = rec.fiscal_document_id._onchange_document_type_id()
                # rec.fiscal_document_id._compute_nfe40_detpag()
                return res
        #res = FiscalDocumentMixin._onchange_document_type_id(self)
        # self._onchange_payment_mode_id()
        return self.fiscal_document_id._onchange_document_type_id()
                                                                                                                                                                   
                                                               
class L10nBrFiscalDocument(models.Model):
    _inherit = "l10n_br_fiscal.document"
    #adicionei novos campos no depends de cada um, com isso, qlqr mudança ja recalcula a tag
    @api.depends("issuer","move_ids","move_ids.payment_mode_id","amount_financial_total","nfe40_tpNF","state_edoc","document_type_id","document_type",)
    def _compute_nfe40_detpag(self):
        return super()._compute_nfe40_detpag()
 
    @api.depends("move_ids","move_ids.due_line_ids","state_edoc","document_type_id","document_type",)
    def _compute_nfe40_dup(self):
        return super()._compute_nfe40_dup()