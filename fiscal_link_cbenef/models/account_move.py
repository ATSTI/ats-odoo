# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


from odoo import models, _, api, fields
from odoo.exceptions import UserError



class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def invoice_validate(self):
        for record in self:
            if (
                record.invoice_line_ids
                and record.product_document_id.id == 31
            ):
                erros = ""
                state = record.env['res.country.state'].search([('code', '=', 'SP')])
                if record.company_id.state_id.id in state.ids:
                    for line in record.invoice_line_ids:
                        if (
                            not line.cbenef_id
                            and line.icms_cst_normal in ['20', '30', '40', '41', '50', '51', '53', '70', '90']
                        ):
                            erros += "\n Erro: Sem beneficio Fiscal (cBenef) ABA ICMS , no item %s" % (line.name)
                if erros and record.date_invoice.strftime('%Y-%m-%d') > '2026-04-05':
                    raise UserError(_(erros))
        return super(AccountInvoice, self).invoice_validate()


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    cbenef_id = fields.Many2one(
        "l10n_br_fiscal.icms.cbenef",
        string="Benefício Fiscal (CST)",
        domain="['|',('cst','=',icms_cst_normal),('cst','=',icms_csosn_simples)]"
    )

    @api.onchange("fiscal_classification_id")
    def _onchange_fiscal_classification_id(self):
        for rec in self:
            if rec.fiscal_classification_id and rec.fiscal_classification_id.cbenef_id:
                rec.cbenef_id = rec.fiscal_classification_id.cbenef_id

    @api.onchange("icms_rule_id")
    def _onchange_icms_rule_id(self):
        for rec in self:
            if rec.invoice_id.fiscal_position_id:
                if rec.icms_rule_id and rec.icms_rule_id.cbenef_id:
                    rec.cbenef_id = rec.icms_rule_id.cbenef_id
                # elif rec.invoice_id.fiscal_position_id and rec.invoice_id.fiscal_position_id.tax_rule_ids:
                #     tax_rule = rec.invoice_id.fiscal_position_id.tax_rule_ids.filtered(lambda r: r.cbenef_id)
                #     if tax_rule:
                #         rec.cbenef_id = tax_rule[0].cbenef_id
                # rec.cbenef_id = rec.fiscal_classification_id.cbenef_id

class AccountFiscalPositionTaxRule(models.Model):
    _inherit = 'account.fiscal.position.tax.rule'

    cbenef_id = fields.Many2one(
        "l10n_br_fiscal.icms.cbenef",
        string="Benefício Fiscal (CST)",
        domain="['|',('cst','=',cst_icms),('cst','=',csosn_icms)]"
    )
