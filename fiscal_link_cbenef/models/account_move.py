# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


from odoo import models, _
from odoo.exceptions import UserError

from odoo.addons.l10n_br_fiscal.constants.fiscal import (
    MODELO_FISCAL_NFE,
 )


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        res = super().action_post()
        for record in self:
            if (
                record.invoice_line_ids
                and record.document_type_id
                and record.document_type_id.code == MODELO_FISCAL_NFE
                and record.issuer == 'company'
            ):
                erros = ""
                state = record.env['res.country.state'].search([('code', '=', 'SP')])
                if record.company_id.state_id.id in state.ids:
                    for line in record.invoice_line_ids:
                        if (
                            not line.cbenef_id
                            and not line.icms_tax_benefit_id
                            and line.icms_cst_id and line.icms_cst_id.code in ['20', '30', '40', '41', '50', '51', '53','70', '90']
                        ):
                            erros += f"\n Erro: Sem beneficio Fiscal (cBenef) ABA ICMS , no item {line.name}"
                if erros and record.invoice_date.strftime('%Y-%m-%d') > '2026-04-05':
                    raise UserError(_(f"{erros}"))
        return res
