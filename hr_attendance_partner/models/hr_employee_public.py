# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class HrEmployeePublic(models.Model):

    _inherit = "hr.employee.public"

    attendance_reason_ids = fields.Char(default='TESTE') 

#     attendance_reason_ids = fields.Many2many(
#         comodel_name="hr.attendance.reason",
#         string="Attendance Reason",
#         help="Specifies the reason for signing In/signing Out in case of "
#         "less or extra hours.",
#     )
# class HrEmployeeBase(models.AbstractModel):
#     _inherit = "hr.employee.base"

       
    
#     @api.model
#     def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
#         fields = fields or []
#         fields += self.env.context.get("extra_fields", [])
#         return super().search_read(
#             domain=domain, fields=fields, offset=offset, limit=limit, order=order
#         )