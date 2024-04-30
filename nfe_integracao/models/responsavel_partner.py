# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from datetime import datetime


class ResPartner(models.Model):
    _inherit = 'res.partner'

    financeiro = fields.Many2one("res.partner", string="Responsavel FInanceiro")