# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import re
from odoo import models, _, api, fields
from odoo.exceptions import UserError

from odoo.addons.l10n_br_fiscal.constants.fiscal import (
    MODELO_FISCAL_NFE,
 )


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        for record in self:
            if record.invoice_line_ids and record.document_type_id and record.document_type_id.code == MODELO_FISCAL_NFE:
                erros = ""
                if record.company_id.state_id.id in record.env['res.country.state'].search([('code', '=', 'SP')]).ids:
                    for line in record.invoice_line_ids:
                        if not line.cbenef_id:
                            erros += f"\n Erro: Sem beneficio Fiscal (cBenef) ABA ICMS , no item {line.name}"
                if erros:
                    raise UserError(_(f"{erros}"))
        return super().action_post()
