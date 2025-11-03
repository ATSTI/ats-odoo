from odoo import models, _, fields
from odoo.addons.l10n_br_fiscal.constants.fiscal import (
    TAX_DOMAIN_IBS,
    TAX_DOMAIN_CBS,
    TAX_DOMAIN_IBSCBS,
    TAX_DOMAIN_IBSUF,
    TAX_DOMAIN_IBSMUN
)

class ResCompany(models.Model):
    _inherit = "res.company"

    ibscbs_cst_id = fields.Many2one(
        comodel_name="l10n_br_fiscal.cst",
        string="CST IBS/CBS",
        domain="[('tax_domain', '=', 'ibscbs')]",
    )
    ibscbs_cst_code = fields.Char(
        related="ibscbs_cst_id.code", string="IBS/CBS CST Code", store=True
    )
    ibsuf_tax_id = fields.Many2one(
        comodel_name="l10n_br_fiscal.tax",
        string="Tax IBS UF",
        domain=[("tax_domain", "=", TAX_DOMAIN_IBSUF)],
    )
    ibsmun_tax_id = fields.Many2one(
        comodel_name="l10n_br_fiscal.tax",
        string="Tax IBS Mun",
        domain=[("tax_domain", "=", TAX_DOMAIN_IBSMUN)],
    )
    cbs_tax_id = fields.Many2one(
        comodel_name="l10n_br_fiscal.tax",
        string="Tax CBS",
        domain=[("tax_domain", "=", TAX_DOMAIN_CBS)],
    )
