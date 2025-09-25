# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class FiscalDocument(models.Model):
    _inherit = "l10n_br_fiscal.document"
    
    date_in_out_option = fields.Datetime(
        string="Data entrada/saída(manual)", copy=False
    )
    
    @api.depends("move_ids", "move_ids.date", "date_in_out_option")
    def _compute_date_in_out(self):
        if self.date_in_out_option:
            self.date_in_out = self.date_in_out_option
        else:
            self.date_in_out = None

    def _inverse_date_in_out(self):
        if self.date_in_out_option:
            self.date_in_out = self.date_in_out_option
        else:
            self.date_in_out = None
