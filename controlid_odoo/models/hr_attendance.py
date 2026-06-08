from odoo import api, fields, models
from odoo import exceptions, _
from datetime import datetime, timedelta
import sys

sys.path.append(
    "/opt/odoo16/external_libs/controlid-relogio-ponto-py"
)

from controlidpy.entities import Session
from controlidpy.functions import get_afds, get_users_from_afds, transform_afds

IN_OR_OUT = ['check_in','check_out','check_in_interval','check_out_interval']

class HrAttendance(models.Model):

    _inherit = 'hr.attendance'

    check_in_interval = fields.Datetime("Entrada de intervalo")
    check_out_interval = fields.Datetime("Saida de intervalo")

    def controlid_get_checkings(self):
        user = self.env['ir.config_parameter'].sudo().get_param('controlid_odoo.user')
        passwd = self.env['ir.config_parameter'].sudo().get_param('controlid_odoo.passwd')
        ip = self.env['ir.config_parameter'].sudo().get_param('controlid_odoo.ip')
        session = Session(user, passwd, ip)
        today = fields.Date.today() - timedelta(days=1)
        afds = get_afds(session, today.day, today.month, today.year)
        users = get_users_from_afds(session, afds)
        final = transform_afds(afds, users)
        
        processed_pis = set()

        for line in final:
            pis = line['pis']

            if pis in processed_pis:
                continue  # já processado

            employee = self.env['hr.employee'].search([
                '|',
                ('cpf_stripped', '=', pis),
                ('name', 'ilike', line['funcionario']),
            ], limit=1)
            if not employee:
                continue

            lines_employee = [x for x in final if x['pis'] == pis]
            
            if len(lines_employee) > len(IN_OR_OUT):
                # loga ou trata o excesso
                lines_employee = lines_employee[:len(IN_OR_OUT)]

            vals = {'employee_id': employee.id}

            for count, line_employee in enumerate(lines_employee):
                dt = datetime.strptime(line_employee['data'], "%d/%m/%Y %H:%M")
                vals[IN_OR_OUT[count]] = dt

            self.create(vals)
            processed_pis.add(pis)

    @api.depends('check_in', 'check_out', 'check_in_interval', 'check_out_interval')
    def _compute_worked_hours(self):
        for attendance in self:
            if attendance.check_out and attendance.check_in:
                delta = attendance.check_out - attendance.check_in
                if attendance.check_in_interval and attendance.check_out_interval:
                    delta -= (attendance.check_out_interval - attendance.check_in_interval)
                attendance.worked_hours = delta.total_seconds() / 3600.0
            else:
                attendance.worked_hours = False

    @api.constrains('check_in_interval', 'check_out_interval')
    def _check_validity_check_in_check_out_interval(self):
        """ verifies if check_in_interval is earlier than check_out_interval. """
        for attendance in self:
            if attendance.check_in_interval and attendance.check_out_interval:
                if attendance.check_out_interval < attendance.check_in_interval:
                    raise exceptions.ValidationError(_('"Check Out Interval" time cannot be earlier than "Check In Interval" time.'))