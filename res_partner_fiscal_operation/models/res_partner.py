from odoo import api, fields, models

class Partner(models.Model):

    _inherit = 'res.partner'

    fiscal_operation_id = fields.Many2one(
        comodel_name="l10n_br_fiscal.operation",
    )