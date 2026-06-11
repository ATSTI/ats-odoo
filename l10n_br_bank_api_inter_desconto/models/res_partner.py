# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    desconto_boleto_inter = fields.Float('Perc. desconto Inter', digits=(16, 2))
