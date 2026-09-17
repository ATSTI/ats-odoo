from odoo import api, models, fields, _
from odoo.exceptions import UserError

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    student_name = fields.Char(string='Nome do Aluno', required=True)
    father_name = fields.Char(string='Nome do Pai')
    mother_name = fields.Char(string='Nome da Mãe')

    school_period = fields.Selection(
        selection=[
            ('matutino', 'Matutino'),
            ('vespertino', 'Vespertino'),
            ('integral', 'Integral'),
        ],
        string='Período Escolar'
    )

    current_school = fields.Char(string='Escola Atual')
    source_indication = fields.Char(string='Indicação')

    tuition_installments = fields.Integer(string='Número de Parcelas')
    material_cost = fields.Float(string='Valor do Material')
    material_installments = fields.Integer(string='Número de Parcelas do Material')

    discount_acquired = fields.Float(string='Desconto Adquirido')
    discount_validity_date = fields.Date(string='Validade do Desconto')

    @api.onchange('student_name')
    def _onchange_student_name(self):
        if self.student_name:
            self.name = f"Visita: {self.student_name}"
