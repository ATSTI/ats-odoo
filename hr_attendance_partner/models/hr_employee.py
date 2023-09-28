# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    cnpj_cpf = fields.Char(related="address_id.cnpj_cpf")
    rg = fields.Char(related="address_id.rg")
