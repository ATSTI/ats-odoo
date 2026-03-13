# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models, fields

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
            if rec.ncm_id:
                rec.cbenef_id = rec.ncm_id.cbenef_id

    @api.onchange("cbenef_id")
    def _onchange_cbenef_id(self):
        for rec in self:
            if not rec.cbenef_id:
                continue
            Tax_Definition = rec.env['l10n_br_fiscal.tax.definition']
            Tax_Group = rec.env['l10n_br_fiscal.tax.group']

            icms_group = Tax_Group.search([('name', '=', 'ICMS')], limit=1)

            tax_benefit = Tax_Definition.search([
                ('is_benefit', '=', True),
                ('code', '=', rec.cbenef_id.code),
                ('tax_group_id', '=', icms_group.id)
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


            rec.icms_tax_benefit_id = tax_benefit.id

    def get_benefit_type(self, cst):
        if cst in ['30', '40']:
            return '1'
        if cst in ['20']:
            return '2'
        if cst in ['51']:
            return '3'
        if cst in ['50']:
            return '4'
        return '0'