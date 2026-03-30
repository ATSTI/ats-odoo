# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    parameter_field = fields.Boolean(string="Parameter Field", compute="_compute_parameter_field")

    def _compute_parameter_field(self):
        for record in self:
            views_posted = self.env['account.move'].search_count([('company_id', '=', record.id), ('invoice_date', '>=', '2026-03-29')])
            if views_posted >= 5:
                record.parameter_field = True
            else:
                record.parameter_field = False