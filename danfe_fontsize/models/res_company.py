# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    danfe_font_size = fields.Boolean(string="Aumentar Fonte do DANFE", default=False)