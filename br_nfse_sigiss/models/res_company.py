# © 2021 Carlos R. Silveira <ats@atsti.com.br, ATS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    client_id = fields.Char(string='Client Id', size=50)
    user_password = fields.Char(string='Senha Acesso', size=50)
    token_nfse = fields.Char(string='Token NFSe')
    validade_token_nfse = fields.Datetime(string='Validade do Token')
