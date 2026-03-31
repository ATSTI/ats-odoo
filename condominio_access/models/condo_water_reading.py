from odoo import fields, api, models
class CondoWaterReading(models.Model):
    _name = "condo.water.reading"
    _description = "Leitura de Água"

    residence_id = fields.Many2one(
        "condo.residence",
        string="Residência",
        ondelete="cascade"
    )

    data_leitura = fields.Date(string="Data da Leitura")
    data_conta = fields.Date(string="Data da Conta")
    valor_conta = fields.Float(string="Valor da Conta")

#     total_agua = fields.Float(
#     string="Total Água",
#     compute="_compute_total_agua",
# )


    # @api.depends('valor_conta')
    # def _compute_total_agua(self):
    #     for rec in self:
    #         rec.total_agua = sum(rec.leitura_agua_ids.mapped('valor_conta'))