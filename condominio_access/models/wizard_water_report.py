# models/wizard_water_report.py

from odoo import models, fields
from datetime import date


class CondoWaterReportWizard(models.TransientModel):
    _name = "condo.water.report.wizard"
    _description = "Relatório de Leituras de Água"

    residence_id = fields.Many2one(
        "condo.residence",
        string="Residência"
    )

    mes = fields.Selection(
        [(str(i), str(i)) for i in range(1, 13)],
        string="Mês",
        required=True
    )

    ano = fields.Integer(
        string="Ano",
        required=True,
        default=lambda self: date.today().year
    )

    metro = fields.Float(
        string="Valor do m³",
        required=True,
        default=3.5
    )

    def _buscar_leituras(self):
        self.ensure_one()

        data_inicio = fields.Date.from_string(
            f"{self.ano}-{int(self.mes):02d}-01"
        )

        if int(self.mes) == 12:
            data_fim = fields.Date.from_string(
                f"{self.ano + 1}-01-01"
            )
        else:
            data_fim = fields.Date.from_string(
                f"{self.ano}-{int(self.mes)+1:02d}-01"
            )

        domain = [
            ("data_referencia", ">=", data_inicio),
            ("data_referencia", "<", data_fim),
        ]

        if self.residence_id:
            domain.append(
                ("residence_id", "=", self.residence_id.id)
            )

        return self.env["condo.water.reading"].search(domain)

    def action_export_pdf(self):

        leituras = self._buscar_leituras()

        return self.env.ref(
            "condominio_access.action_report_water_reading"
        ).report_action(
            self,
            data={
                "ids": leituras.ids,
                "metro": self.metro,
            }
        )
