
from odoo import models, _, api, fields
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = "account.move"
    _inherits = {"l10n_br_fiscal.document": "fiscal_document_id"}
    
    ibscbs = fields.Boolean('IBSCBS')
