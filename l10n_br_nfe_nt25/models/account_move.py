
from odoo import models, _, api, fields
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = "account.move"
    _inherits = {"l10n_br_fiscal.document": "fiscal_document_id"}
    
    # IBSCBS
    ibscbs_cst_id = fields.Many2one(
        comodel_name="ibs_cbs.cst",
        string="CST-IBS/CBS",
    )
    ibscbs_classtrib_id = fields.Many2one(
        comodel_name="ibs_cbs.classtrib",
        string="Classificação Tributária",
    )

