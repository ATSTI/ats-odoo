# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, models


class FreteReportXslx(models.AbstractModel):
    _name = "report.relatorio_frete.frete_report_xlsx"
    _description = "Frete Report XLSX Report"
    _inherit = "report.account_financial_report.abstract_report_xlsx"

    def _get_report_name(self, report, data):
        company_id = data.get("company_id", False)
        report_name = _("Relatório de Frete")
        if company_id:
            company = self.env["res.company"].browse(company_id)
            suffix = " - {} - {}".format(company.name, company.currency_id.name)
            report_name = report_name + suffix
        return report_name

    def _get_report_columns(self, report):
        return {
            0: {"header": _("Fatura"), "field": "name", "width": 20},
            1: {"header": _("Documento"), "field": "document_number", "width": 20},
            2: {"header": _("Parceiro"), "field": "partner_id", "width": 60},
            3: {"header": _("Valor Frete/Receita"), "field": "balance", "type": "amount", "width": 25},
        }

    def _get_report_filters(self, report):
        return [
            [_("Data inicio"), report.date_from.strftime("%d/%m/%Y")],
            [_("Data fim"), report.date_to.strftime("%d/%m/%Y")],
            [_("Contas"), report.account_ids.mapped("name")[0]],
        ]

    def _get_col_count_filter_name(self):
        return 0

    def _get_col_count_filter_value(self):
        return 2

    def _generate_report_content(self, workbook, report, data, report_data):
        res_data = self.env[
            "report.relatorio_frete.frete_report"
        ]._get_report_values(report, data)
        frete_report = res_data["frete_report"]
        notas = res_data["notas"]
        self.write_array_header(report_data)
        total_geral = 0
        for despesa in frete_report:
            # Write taxtag line
            despesa["balance"] = (-1) * despesa["balance"]
            self.write_line_from_dict(despesa, report_data)
            # mostrando as receitas
            total = despesa['balance']
            for line in notas:
                if line["despesa_id"] == despesa["move_id"]:
                    line["balance"] = line["amount_freight_value"]
                    total += line["balance"]
                    line["name"] = line["sale_id"]
                    self.write_line_from_dict(line, report_data)
            # Write total line
            # total_line = {
            #     "name": _("Total"),
            #     "balance": total,
            # }
            # self.write_line_from_dict(total_line, report_data)
            total_geral += total
            # report_data["sheet"].write_string(
            #         report_data["row_pos"],
            #         3,
            #         '---------------',
            #         report_data["formats"]["format_right_bold_italic"],
            #     )
            # report_data["row_pos"] += 1            
            report_data["sheet"].write_number(
                    report_data["row_pos"],
                    3,
                    total,
                    report_data["formats"]["format_amount_bold"],
                )
            report_data["row_pos"] += 1
        # self.write_array_header(report_data)
        # total_line = {
        #     "name": _("Resultado Final"),
        #     "balance": total_geral,
        # }       
        # self.write_line_from_dict(total_line, report_data)
        report_data["sheet"].write_string(
                report_data["row_pos"],
                2,
                'Resultado Final',
                report_data["formats"]["format_right_bold_italic"],
            )
        report_data["sheet"].write_number(
                report_data["row_pos"],
                3,
                total_geral,
                report_data["formats"]["format_amount_bold"],
            )
