from odoo import fields, api, models


class CondoResidenceLogs(models.Model):
    _name = "condo.residence.logs"
    _description = "Modelo para receber os logs da controladora"

    residence_id = fields.Many2one(
        "condo.residence",
        string="Residência",
        ondelete="cascade",
        required=True,
    )




    