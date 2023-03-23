# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields



class Partner(models.Model):
    _inherit = "res.partner"

    vehicle_ids = fields.One2many(
        comodel_name='repair.vehicle',
        inverse_name='partner_id',
        string="Veículos",
        copy=True, auto_join=True
    )