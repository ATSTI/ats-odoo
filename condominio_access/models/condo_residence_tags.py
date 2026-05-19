from odoo import fields, api, models


class CondoResidenceTags(models.Model):
    _name = "condo.residence.tags"
    _description = "Tags"

    residence_id = fields.Many2one(
        "condo.residence",
        string="Residência",
        ondelete="cascade",
        required=True,
    )

    name = fields.Text("Descrição")
    
    numero_tag = fields.Char("Número da TAG")

    _sql_constraints = [
        (
            "unique_tag_per_residence",
            "unique(residence_id, numero_tag)",
            "Esta TAG já está cadastrada para esta residência.",
        )
    ]

    