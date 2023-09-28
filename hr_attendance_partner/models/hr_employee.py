# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    attendance_reason_ids = fields.Char(default='TESTE x') 
