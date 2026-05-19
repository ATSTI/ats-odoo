from odoo import fields, api, models
from datetime import timedelta


class CondoWaterReading(models.Model):
    _name = "condo.water.reading"
    _description = "Leitura de Água"

    residence_id = fields.Many2one(
        "condo.residence",
        string="Residência",
        ondelete="cascade"
    )

    data_referencia = fields.Date(
        string="Mês Referência",
        help="""
        Data usada para identificar o mês da leitura.
        """
    )

    anterior = fields.Float(string="Anterior")

    atual = fields.Float(string="Atual")

    consumo = fields.Float(
        string="Consumo",
        compute="_compute_consumo",
        store=True)

    obs = fields.Text(string="Observações")

    @api.depends("atual", "anterior")
    def _compute_consumo(self):
        for rec in self:
            rec.consumo = abs(rec.atual - rec.anterior)

    # @api.onchange("residence_id", "data_referencia")
    # def _onchange_buscar_leitura_anterior(self):

    #     if not self.residence_id or not self.data_referencia:
    #         return

    #     leitura_anterior = self.env["condo.water.reading"].search(
    #         [
    #             ("residence_id", "=", self.residence_id.id),
    #             ("data_referencia", "<", self.data_referencia),
    #         ],
    #         order="data_referencia desc",
    #         limit=1
    #     )

    #     if leitura_anterior:
    #         self.anterior = leitura_anterior.atual