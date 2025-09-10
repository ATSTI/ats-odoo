# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, _, api, fields


class IbsCbsCst(models.Model):
    _name = "ibs_cbs.cst"

    name = fields.Char("Descrição", required=True)
    code = fields.Char("Código", required=True)
    ibs_aliquota = fields.Float("Alíquota (%)", required=True)
    cbs_aliquota = fields.Float("Alíquota (%)", required=True)


class IbsCbsClassTrib(models.Model):
    _name = "ibs_cbs.classtrib"

    name = fields.Char("Descrição", required=True)
    code = fields.Char("Código", required=True)

