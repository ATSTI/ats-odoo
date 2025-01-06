# License AGPL-3 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class FiscalDocument(models.Model):
    _inherit = "l10n_br_fiscal.document"

    close_id = fields.Many2one(comodel_name="l10n_br_fiscal.closing", string="Close ID", copy=False)