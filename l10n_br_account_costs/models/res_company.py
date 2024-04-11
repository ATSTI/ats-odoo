# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    acc_freight_id = fields.Many2one(comodel_name="account.account", string="Frete")
    acc_other_id = fields.Many2one(comodel_name="account.account", string="Outro")
    acc_insurance_id = fields.Many2one(comodel_name="account.account", string="Seguro")

