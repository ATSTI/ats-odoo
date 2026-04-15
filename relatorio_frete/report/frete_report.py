# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import operator

from odoo import api, fields, models


class FreteReport(models.AbstractModel):
    _inherit = "report.account_financial_report.abstract_report"
    _name = "report.relatorio_frete.frete_report"
    _description = "Frete Report"

    @api.model
    def _get_frete_report_domain(self, company_id, date_from, date_to, only_posted_moves, accounts_ids=None):
        domain = [
            ("company_id", "=", company_id),
            ("date", ">=", date_from),
            ("date", "<=", date_to),
            ("account_id", "in", accounts_ids),
            ("journal_id.type", "=", "purchase"),
        ]
        if only_posted_moves:
            domain += [("move_id.state", "=", "posted")]
        else:
            domain += [("move_id.state", "in", ["posted", "draft"])]
        return domain

    def _get_frete_report_data(self, company_id, date_from, date_to, accounts_ids=None):
        frete_domain = self._get_frete_report_domain(
            company_id, date_from, date_to, True, accounts_ids
        )
        ml_fields = self._get_ml_fields_frete_report()

        # linhas com frete
        frete_move_lines = self.env["account.move.line"].search_read(
            domain=frete_domain,
            fields=ml_fields,
        )
        despesa_data = []
        receita_data = []
        
        for move in frete_move_lines:
            am = self.env["account.move"].browse(move["move_id"][0])
            move_id = am.id
            despesa_data.append(
                {
                    "id": move["id"],
                    "name": am.name,
                    "document_number": am.document_number,
                    "account_id": move["account_id"][0],
                    "debit": move["debit"],
                    "credit": move["credit"],
                    "partner_id": move["partner_id"][1] if move["partner_id"] else False,
                    "move_id": move_id,
                }
            )
            for related_doc in am.document_related_ids:
                move_doc = related_doc.document_related_id
                sale_id = move_doc.move_ids.line_ids.sale_line_ids.order_id
                receita_data.append(
                    {
                        "id": move_doc.id,
                        "partner_id": move_doc.partner_id.name if move_doc.partner_id else False,
                        "document_date": fields.Date.from_string(move_doc.document_date),
                        "amount_freight_value": move_doc.amount_freight_value,
                        "move_ids": move_doc.move_ids.id,
                        "document_number": move_doc.document_number,
                        "sale_id": sale_id.name if sale_id else False,
                        "despesa_id": move_id,
                    }
                )
        return despesa_data, receita_data

    def _get_frete_report_tag_data(self, despesa_data, receita_data):
        frete_report = {}
        frete_report_list = []
        for move_line in despesa_data:
            move_id = move_line["move_id"]
            frete_report[move_id] = {}
            frete_report[move_id]["balance"] = move_line["debit"]
            frete_report[move_id]["partner_id"] = move_line["partner_id"]
            frete_report[move_id]["account_id"] = move_line["account_id"]
            frete_report[move_id]["move_id"] = move_id
            frete_report[move_id]["document_number"] = move_line["document_number"]
            frete_report[move_id]["name"] = move_line["name"]
            frete_report_list.append(frete_report[move_id])
        return frete_report_list

    def _get_frete_report_receita_data(self, despesa_data, receita_data):
        frete_report = {}
        frete_report_list = []
        for rec in receita_data:
            move_id = rec["move_ids"]
            frete_report[move_id] = {}
            frete_report[move_id]["id"] = rec["id"]
            frete_report[move_id]["amount_freight_value"] = rec["amount_freight_value"]
            frete_report[move_id]["document_date"] = rec["document_date"]
            frete_report[move_id]["partner_id"] = rec["partner_id"]
            frete_report[move_id]["document_number"] = rec["document_number"]
            frete_report[move_id]["despesa_id"] = rec["despesa_id"]
            frete_report[move_id]["sale_id"] = rec["sale_id"]
            frete_report_list.append(frete_report[move_id])
        return frete_report_list

    def _get_report_values(self, docids, data):
        res = super()._get_report_values(docids, data)
        wizard_id = data["wizard_id"]
        company = self.env["res.company"].browse(data["company_id"])
        company_id = data["company_id"]
        date_from = fields.Date.from_string(data["date_from"])
        date_to = fields.Date.from_string(data["date_to"])
        accounts_ids = data.get("account_ids", None)
        despesa_data, receita_data = self._get_frete_report_data(
            company_id, date_from, date_to, accounts_ids=accounts_ids
        )
        frete_report = self._get_frete_report_tag_data(
            despesa_data, receita_data
        )
        receita_report = self._get_frete_report_receita_data(
            despesa_data, receita_data
        )
        res.update(
            {
                "doc_ids": [wizard_id],
                "doc_model": "frete.report.wizard",
                "docs": self.env["frete.report.wizard"].browse(wizard_id),
                "company_name": company.display_name,
                "currency_name": company.currency_id.name,
                "date_from": date_from,
                "date_to": date_to,
                "account_ids": accounts_ids,
                "frete_report": frete_report,
                "notas": receita_report,
            }
        )
        return res

    def _get_ml_fields_frete_report(self):
        return [
            "id",
            "name",
            "account_id",
            "debit",
            "credit",
            "partner_id",
            "move_id",
            "balance",
            "document_number",
        ]
