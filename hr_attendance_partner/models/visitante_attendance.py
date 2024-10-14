
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from datetime import datetime, timedelta

from odoo import api, fields, models


class VisitanteAttendance(models.TransientModel):
    _name = "visitante.attendance"

    name = fields.Char("Nome")

    def action_create_attendance(self):
        hr = self.env['hr.employee']
        vals = {
            'name': self.name
        }
        hr.create(vals)
        return True

class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    def action_visitante_cadastra(self):
        return {'type': 'ir.actions.act_window',
               'name': _('Mark as Done'),
               'res_model': 'visitante.attendance',
               'target': 'new',
               'view_id': self.env.ref('visitante_create_wizard_view').id,
               'view_mode': 'form',
            #    'context': {'default_produce_line_ids': lines}
               }
