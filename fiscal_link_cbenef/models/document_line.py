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

    def _prepare_fields_icms(self, tax_dict):
        res = super()._prepare_fields_icms(tax_dict)
        for rec in self:
            if (
                rec.icms_cst_id
                and rec.move_id.issuer == DOCUMENT_ISSUER_COMPANY
                and rec.cbenef_id
            ):
                # if rec.get_benefit_type(rec.icms_cst_id.code) != '0':
                cbenefs = rec.env['l10n_br_fiscal.icms.cbenef'].search([('icms_cst_ids', 'in', rec.icms_cst_id.id)])
                if rec.cbenef_id in cbenefs:
                    Tax_Definition = rec.env['l10n_br_fiscal.tax.definition']
                    tax_benefit = Tax_Definition.search([
                        ('is_benefit', '=', True),
                        ('cst_id', '=', rec.icms_cst_id.id),
                        ('tax_group_id', '=', rec.icms_cst_id.tax_group_id.id),
                        ('fiscal_operation_line_id', '=', rec.fiscal_operation_line_id.id),
                    ], limit=1)
                    if tax_benefit:
                        rec.icms_tax_benefit_id = tax_benefit.id
                else:
                    rec.cbenef_id = False
                    rec.icms_tax_benefit_id = False
        return res

    @api.depends("cbenef_id")
    def _compute_fiscal_tax_ids(self):
        for rec in self:
            if not rec.cbenef_id:
                continue
            if rec.cbenef_id.code == 'SP00SEMCBENEF' or not rec.cbenef_id.code:
                rec.icms_tax_benefit_id = False
                continue
            if rec.ncm_id and not rec.ncm_id.cbenef_id:
                rec.ncm_id.cbenef_id = rec.cbenef_id.id
            Tax_Definition = rec.env['l10n_br_fiscal.tax.definition']
            Tax_Group = rec.env['l10n_br_fiscal.tax.group']

            icms_group = Tax_Group.search([('name', '=', 'ICMS')], limit=1)
            
            tax_benefit = Tax_Definition.search([
                ('is_benefit', '=', True),                
                ('tax_domain', '=', 'icms'),
                ('code', '=', rec.cbenef_id.code),
            ], limit=1)

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
            # ACREDITO q isso aqui abaixo poderia levar o usuario a fazer coisa errada, se quiser mudar tem q entrar no NCM e mudar.
            # else:
                # if tax_benefit.code != rec.cbenef_id.code:
                    # rec.cbenef_id = False
                    # erros = "Já existe um benefício fiscal cadastrado para essa CST, altere a linha da operação fiscal e o cBenef no NCM se existir."
                    # raise UserError(_(f"{erros}"))
                    # tax_benefit.write({
                    #     'code': rec.cbenef_id.code,
                    #     'description': rec.cbenef_id.description,
                    #     'benefit_type': rec.get_benefit_type(
                    #         rec.icms_cst_id.code if rec.icms_cst_id else False
                    #     ),
                    #     'state_from_id': rec.env['res.country.state'].search([('code', '=', 'SP')], limit=1).id,
                    # })
                    # tax_benefit.display_name = f"{icms_group.name} - f{rec.icms_cst_id.code} - {rec.cbenef_id.code} - {rec.cbenef_id.description}"
                    # tax_benefit._onchange_tax_id()
            if rec.ncm_id and not rec.ncm_id.cbenef_id:
                rec.ncm_id.cbenef_id = rec.cbenef_id.id

            rec.icms_tax_benefit_id = tax_benefit.id
        return super()._compute_fiscal_tax_ids()

    def get_benefit_type(self, cst):
        if cst in ['30', '40']:
            return '1'
        if cst in ['20']:
            return '2'
        if cst in ['51']:
            return '3'
        if cst in ['41']:
            return '7'        
        if cst in ['50']:
            return '4'
        if cst in ['90']:
            return '9'
        return '0'