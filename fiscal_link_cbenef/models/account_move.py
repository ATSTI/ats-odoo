# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import re
from odoo import models, _, api, fields

from odoo.addons.l10n_br_fiscal.constants.fiscal import (
    MODELO_FISCAL_NFE,
 )


class AccountMove(models.Model):
    _inherit = "account.move"
  
    @api.onchange("invoice_line_ids")
    def _onchange_invoice_line_ids(self):
        if self.invoice_line_ids and self.document_type_id and self.document_type_id.code == MODELO_FISCAL_NFE:
            erros = self.xml_error_message or ""
            if self.company_id.state_id == self.env['res.country.state'].search([('code', '=', 'SP')], limit=1):
                for line in self.invoice_line_ids:
                    if not line.cbenef_id:
                        erros += f"\n Erro: Sem beneficio Fiscal (cBenef) ABA ICMS , no item {line.name}"
                self.xml_error_message = erros or False
