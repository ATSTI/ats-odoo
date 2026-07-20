from odoo import api, fields, models
from odoo import exceptions, _

class HrEmployee(models.Model):

    _inherit = 'hr.employee'

    cpf_stripped = fields.Char(
        "CPF Stripped",
        compute="_compute_cpf_stripped",
        store=True,
        groups="hr.group_hr_user",
    )

    @api.depends('cpf')
    def _compute_cpf_stripped(self):
        for rec in self:
            if rec.cpf:
                rec.cpf_stripped = ''.join(filter(str.isdigit, rec.cpf))
            else:
                rec.cpf_stripped = False