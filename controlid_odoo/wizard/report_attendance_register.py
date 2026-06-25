
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, time
 
 
class ReportAttendanceRegister(models.TransientModel):
    _name = "report.attendance.register"
    _description = "Imprimir Relatório de Relógio de Ponto"
 
    employee_ids = fields.Many2many(
        comodel_name="hr.employee",
        string="Funcionários",
    )
    date_from = fields.Date(
        string="De",
        required=True,
    )
    date_to = fields.Date(
        string="Até",
        required=True,
    )
 
    attendance_ids = fields.Many2many(
        comodel_name="hr.attendance",
        string="Registros de Ponto",
        compute="_compute_attendance_ids",
    )
 
    @api.depends("employee_ids", "date_from", "date_to")
    def _compute_attendance_ids(self):
        for rec in self:
            if rec.employee_ids and rec.date_from and rec.date_to:
                rec.attendance_ids = self.env["hr.attendance"].search([
                    ("employee_id", "in", rec.employee_ids.ids),
                    ("check_in", ">=", str(rec.date_from) + " 00:00:00"),
                    ("check_out", "<=", str(rec.date_to) + " 23:59:59"),
                ])
            else:
                rec.attendance_ids = False

    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        for rec in self:
            if rec.date_from and rec.date_to and rec.date_from > rec.date_to:
                raise ValidationError("A data 'De' não pode ser maior que a data 'Até'.")
 

    def action_print_report(self):
        self.ensure_one()
        if not self.employee_ids:
            raise ValidationError("Selecione ao menos um funcionário.")
        if not self.date_from or not self.date_to:
            raise ValidationError("Informe o período (De / Até).")

        data = {
            'date_from': str(self.date_from),
            'date_to': str(self.date_to),
            'employee_ids': self.employee_ids.ids,
            'attendance_ids': self.attendance_ids.ids,
        }
        return self.env.ref('controlid_odoo.report_controlid_attendance').report_action(self)
    
    def check_is_work_day(self, day):
        if day:
            # No Python: 5 = Sábado, 6 = Domingo
            if day.weekday() == 5:
                return "SAB"
            elif day.weekday() == 6:
                return "DOM"
            else:
                # Configura o início e o fim do dia para buscar no Datetime do Odoo
                start_of_day = datetime.combine(day, time.min)
                end_of_day = datetime.combine(day, time.max)
                
                day_off = self.env['resource.calendar.leaves'].search([
                    ('date_from', '<=', end_of_day),
                    ('date_to', '>=', start_of_day),
                ], limit=1) # Usar limit=1 evita carregar múltiplos registros sem necessidade
                
                if day_off:
                    return "FER"
        return ""
