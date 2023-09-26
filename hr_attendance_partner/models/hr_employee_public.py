# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrEmployeePublic(models.Model):

    _inherit = "hr.employee.public"

    def action_partner_create(self):
        pass