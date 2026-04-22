# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class FreteReportWizard(models.TransientModel):
    _name = "frete.report.wizard"
    _description = "Relatorio de Frete(Despesa x Receita)"
    _inherit = "account_financial_report_abstract_wizard"

    date_range_id = fields.Many2one(comodel_name="date.range", string="Período")
    date_from = fields.Date("Data inicio", required=True)
    date_to = fields.Date("Data fim", required=True)

    account_ids = fields.Many2many(
        comodel_name="account.account", string="Contas Despesas de Frete"
    )

    @api.onchange("company_id")
    def onchange_company_id(self):
        if (
            self.company_id
            and self.date_range_id.company_id
            and self.date_range_id.company_id != self.company_id
        ):
            self.date_range_id = False
        res = {"domain": {"date_range_id": []}}
        if not self.company_id:
            return res
        else:
            res["domain"]["date_range_id"] += [
                "|",
                ("company_id", "=", self.company_id.id),
                ("company_id", "=", False),
            ]
        return res

    @api.onchange("date_range_id")
    def onchange_date_range_id(self):
        """Handle date range change."""
        self.date_from = self.date_range_id.date_start
        self.date_to = self.date_range_id.date_end

    @api.constrains("company_id", "date_range_id")
    def _check_company_id_date_range_id(self):
        for rec in self.sudo():
            if (
                rec.company_id
                and rec.date_range_id.company_id
                and rec.company_id != rec.date_range_id.company_id
            ):
                raise ValidationError(
                    _(
                        "The Company in the Vat Report Wizard and in "
                        "Date Range must be the same."
                    )
                )

    def _print_report(self, report_type):
        self.ensure_one()
        data = self._prepare_report_data()
        if report_type == "xlsx":
            report_name = "relatorio_frete.frete_report_xlsx"
        else:
            report_name = "relatorio_frete.frete_report"
        return (
            self.env["ir.actions.report"]
            .search(
                [("report_name", "=", report_name), ("report_type", "=", report_type)],
                limit=1,
            )
            .report_action(self, data=data)
        )

    def _prepare_report_data(self):
        res = super()._prepare_report_data()
        res.update(
            {
                "company_id": self.company_id.id,
                "date_from": self.date_from,
                "date_to": self.date_to,
                "account_ids": self.account_ids.ids,
                "account_financial_report_lang": self.env.lang,
            }
        )
        return res

    def _export(self, report_type):
        """Default export is PDF."""
        return self._print_report(report_type)
