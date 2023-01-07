# © 2021 Carlos R. Silveira <ats@atsti.com.br, ATS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class BrAccountServiceType(models.Model):
    _inherit = 'br_account.service.type'

    codigo_tributacao_municipio = fields.Char(
        string=u"Cód. Tribut. Munic.", size=20,
        help="Código de Tributação no Munípio")
