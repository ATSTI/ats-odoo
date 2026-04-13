# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models, _, fields
from odoo.exceptions import UserError

from odoo.addons.l10n_br_fiscal.constants.fiscal import (
    DOCUMENT_ISSUER_COMPANY,
)

class DocumentLineMixin(models.AbstractModel):
    _inherit = "l10n_br_fiscal.document.line.mixin"

    cbenef_id = fields.Many2one(
        "l10n_br_fiscal.icms.cbenef",
        string="Benefício Fiscal (CST)",
        domain="[('icms_cst_ids','in',icms_cst_id)]"
    )

class DocumentLineMixinMethods(models.AbstractModel):
    _inherit = "l10n_br_fiscal.document.line.mixin.methods"

    @api.onchange("ncm_id")
    def _onchange_ncm_id(self):
        for rec in self:
            if rec.ncm_id and rec.ncm_id.cbenef_id:
                cbenefs = rec.env['l10n_br_fiscal.icms.cbenef'].search([
                    ('icms_cst_ids', 'in', rec.icms_cst_id.id)
                ])
                if rec.ncm_id.cbenef_id in cbenefs:
                    rec.cbenef_id = rec.ncm_id.cbenef_id
                else:
                    rec.cbenef_id = False

    def _search_tax_definition(self, cst_id, tax_group_id, fiscal_operation_line_id, code=None):
        domain = [
            ('is_benefit', '=', True),
            ('cst_id', '=', cst_id),
            ('tax_group_id', '=', tax_group_id),
            ('fiscal_operation_line_id', '=', fiscal_operation_line_id),
        ]
        if code:
            domain.append(('code', '=', code))
        Tax_Definition = self.env['l10n_br_fiscal.tax.definition']
        tax_benefit = Tax_Definition.search(domain, limit=1)
        return tax_benefit

    def _search_cbnef(self):
        for rec in self:
            if not rec.product_id:
                continue
            # necessario para o pedido de venda, pois o move_id só existe no momento da criação da fatura,
            # e o pedido de venda é criado antes da fatura
            if 'move_id' not in rec._fields:
                cond = rec.icms_cst_id and rec.cbenef_id
            else:
                cond = rec.icms_cst_id and rec.cbenef_id and rec.move_id.issuer == DOCUMENT_ISSUER_COMPANY
            if cond:
                cbenef = self.get_benefit_type(
                        rec.icms_cst_id.code if rec.icms_cst_id else False
                )
                if cbenef != '0':
                    cbenefs = rec.env['l10n_br_fiscal.icms.cbenef'].search([('icms_cst_ids', 'in', rec.icms_cst_id.id)])
                    if rec.cbenef_id and rec.cbenef_id in cbenefs:
                        if rec.ncm_id and not rec.ncm_id.cbenef_id:
                            rec.ncm_id.cbenef_id = rec.cbenef_id.id

                        tax_benefit = rec._search_tax_definition(
                            rec.icms_cst_id.id,
                            rec.icms_cst_id.tax_group_id.id,
                            rec.fiscal_operation_line_id.id,
                            None,
                        )

                        if tax_benefit:
                            rec.icms_tax_benefit_id = tax_benefit.id
                        else:
                            rec._onchange_cbenef_id()
                    else:
                        rec.cbenef_id = False
                        rec.icms_tax_benefit_id = False
            else:
                if rec.fiscal_operation_line_id:
                    for tax in rec.fiscal_operation_line_id.tax_definition_ids:
                        if tax.is_benefit:
                            if  tax.tax_domain == 'icms' or tax.tax_domain == 'icmssn':
                                tax_benefit = rec._search_tax_definition(
                                    rec.icms_cst_id.id,
                                    rec.icms_cst_id.tax_group_id.id,
                                    rec.fiscal_operation_line_id.id,
                                    None,
                                )
                                # rec.cbenef_id = tax_benefit.id
                                rec.icms_tax_benefit_id = tax_benefit.id
                            break

    @api.onchange(
        "fiscal_operation_id", "ncm_id", "nbs_id", "cest_id", "service_type_id"
    )
    def _onchange_fiscal_operation_id(self):
        """Ao alterar o campo fiscal_operation_id, são atualizados os impostos fiscais relacionados"""
        result = super()._onchange_fiscal_operation_id()

        self._search_cbnef()
        return result

    @api.onchange("cbenef_id")
    def _onchange_cbenef_id(self):
        for rec in self:
            if not rec.cbenef_id or not rec.icms_cst_id or not rec.fiscal_operation_line_id:
                continue
            if rec.ncm_id and not rec.ncm_id.cbenef_id:
                rec.ncm_id.cbenef_id = rec.cbenef_id.id
            Tax_Definition = rec.env['l10n_br_fiscal.tax.definition']
            Tax_Group = rec.env['l10n_br_fiscal.tax.group']

            icms_group = Tax_Group.search([('name', 'in', ['ICMS', 'ICMSSN'])], limit=1)
            
            tax_benefit = rec._search_tax_definition(
                rec.icms_cst_id.id,
                rec.icms_cst_id.tax_group_id.id,
                rec.fiscal_operation_line_id.id,
                rec.cbenef_id.code,
            )

            if not tax_benefit:
                tax_benefit = Tax_Definition.create({
                    'tax_group_id': icms_group.id,
                    'custom_tax': True,
                    'tax_id': rec.icms_tax_id.id,
                    'is_benefit': True,
                    'code': rec.cbenef_id.code,
                    'description': rec.cbenef_id.description,
                    'benefit_type': rec.get_benefit_type(
                        rec.icms_cst_id.code if rec.icms_cst_id else False
                    ),
                    'state_from_id': rec.env['res.country.state'].search([('code', '=', 'SP')], limit=1).id,
                })
                tax_benefit.display_name = f"{icms_group.name} - f{rec.icms_cst_id.code} - {rec.cbenef_id.code} - {rec.cbenef_id.description}"
                tax_benefit._onchange_tax_id()
            if rec.ncm_id and not rec.ncm_id.cbenef_id:
                rec.ncm_id.cbenef_id = rec.cbenef_id.id

            rec.icms_tax_benefit_id = tax_benefit[0].id

    def get_benefit_type(self, cst):
        if cst in ['30', '40']:
            return '1'
        if cst in ['20']:
            return '2'  
        if cst in ['50']:
            return '4'
        if cst in ['51', '53']:
            return '5'
        if cst in ['41']:
            return '7' 
        if cst in ['90']:
            return '9'
        return '0'