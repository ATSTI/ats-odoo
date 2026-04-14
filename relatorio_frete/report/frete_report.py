# Copyright  2018 Forest and Biomass Romania
# Copyright 2020 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import operator

from odoo import api, fields, models


class FreteReport(models.AbstractModel):
    _inherit = "report.account_financial_report.abstract_report"
    _name = "report.relatorio_frete.frete_report"
    _description = "Frete Report"

    def _get_receitas(self, document_ids):
        # import pudb;pu.db        
        taxes = self.env["account.tax"].browse(tax_ids)
        tax_data = {}
        for tax in taxes:
            tax_data.update(
                {
                    tax.id: {
                        "id": tax.id,
                        "name": tax.name,
                        "tax_group_id": tax.tax_group_id.id,
                        "type_tax_use": tax.type_tax_use,
                        "amount_type": tax.amount_type,
                        "tags_ids": tax.invoice_repartition_line_ids.tag_ids.ids,
                    }
                }
            )
        return tax_data

    @api.model
    def _get_frete_report_domain(self, company_id, date_from, date_to, only_posted_moves, accounts_ids=None):
        # import pudb;pu.db
        domain = [
            ("company_id", "=", company_id),
            ("date", ">=", date_from),
            ("date", "<=", date_to),
            ("account_id", "in", accounts_ids),
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
        related_data = []
        for move_id in frete_move_lines:
            related_data.append(move_id["move_id"][0])
        related_data = list(set(related_data))
        
        # documentos fiscais com os documentos relacionados
        doc_domain = [
            ("move_ids", "in", related_data),
        ]        
        import pudb;pu.db
        move_fields = ["id", "document_date", "partner_id", "document_related_ids"]
        move_ids = self.env["l10n_br_fiscal.document"].search_read(
            domain=doc_domain,
            fields=move_fields,
        )
        # documentos relacionados
        doc_data = []
        for move_doc in move_ids:
            doc_data.append(move_doc["document_related_ids"][0])
        doc_data = list(set(doc_data))            

        # lendo documentos relacionados
        related_domain = [
            ("id", "in", doc_data),
        ]        
        import pudb;pu.db
        doc_fields = ["id", "partner_id", "document_date", "amount_freight_value"]
        doc_ids = self.env["l10n_br_fiscal.document"].search_read(
            domain=related_domain,
            fields=doc_fields,
        )
        receita_data = []
        for move_doc in doc_ids:
             receita_data.append(move_doc)
        # tax_ids = list(map(operator.itemgetter("tax_line_id"), vat_data))
        # tax_ids = list(set(tax_ids))
        # tax_data = self._get_receitas(document_ids)
        return related_data, receita_data

    def _get_tax_group_data(self, tax_group_ids):
        # import pudb;pu.db
        tax_groups = self.env["account.tax.group"].browse(tax_group_ids)
        tax_group_data = {}
        for tax_group in tax_groups:
            tax_group_data.update(
                {
                    tax_group.id: {
                        "id": tax_group.id,
                        "name": tax_group.name,
                        "code": str(tax_group.sequence),
                    }
                }
            )
        return tax_group_data

    def _get_frete_report_group_data(self, vat_report_data, tax_data, tax_detail):
        # import pudb;pu.db        
        vat_report = {}
        for tax_move_line in vat_report_data:
            tax_id = tax_move_line["tax_line_id"]
            if tax_data[tax_id]["amount_type"] == "group":
                pass
            else:
                tax_group_id = tax_data[tax_id]["tax_group_id"]
                if tax_group_id not in vat_report.keys():
                    vat_report[tax_group_id] = {}
                    vat_report[tax_group_id]["net"] = 0.0
                    vat_report[tax_group_id]["tax"] = 0.0
                    vat_report[tax_group_id][tax_id] = dict(tax_data[tax_id])
                    vat_report[tax_group_id][tax_id].update({"net": 0.0, "tax": 0.0})
                else:
                    if tax_id not in vat_report[tax_group_id].keys():
                        vat_report[tax_group_id][tax_id] = dict(tax_data[tax_id])
                        vat_report[tax_group_id][tax_id].update(
                            {"net": 0.0, "tax": 0.0}
                        )
                vat_report[tax_group_id]["net"] += tax_move_line["net"]
                vat_report[tax_group_id]["tax"] += tax_move_line["tax"]
                vat_report[tax_group_id][tax_id]["net"] += tax_move_line["net"]
                vat_report[tax_group_id][tax_id]["tax"] += tax_move_line["tax"]
        tax_group_data = self._get_tax_group_data(vat_report.keys())
        vat_report_list = []
        for tax_group_id in vat_report.keys():
            vat_report[tax_group_id]["name"] = tax_group_data[tax_group_id]["name"]
            vat_report[tax_group_id]["code"] = tax_group_data[tax_group_id]["code"]
            if tax_detail:
                vat_report[tax_group_id]["taxes"] = []
                for tax_id in vat_report[tax_group_id]:
                    if isinstance(tax_id, int):
                        vat_report[tax_group_id]["taxes"].append(
                            vat_report[tax_group_id][tax_id]
                        )
            vat_report_list.append(vat_report[tax_group_id])
        return vat_report_list

    def _get_tags_data(self, tags_ids):
        # import pudb;pu.db
        tags = self.env["account.account.tag"].browse(tags_ids)
        tags_data = {}
        for tag in tags:
            tags_data.update({tag.id: {"code": "", "name": tag.name}})
        return tags_data

    def _get_frete_report_tag_data(self, frete_report_data, tax_data, tax_detail):
        # import pudb;pu.db
        frete_report = {}
        for tax_move_line in frete_report_data:
            tax_id = tax_move_line["tax_line_id"]
            tags_ids = tax_data[tax_id]["tags_ids"]
            if tax_data[tax_id]["amount_type"] == "group":
                continue
            else:
                if tags_ids:
                    for tag_id in tags_ids:
                        if tag_id not in frete_report.keys():
                            frete_report[tag_id] = {}
                            frete_report[tag_id]["net"] = 0.0
                            frete_report[tag_id]["tax"] = 0.0
                            frete_report[tag_id][tax_id] = dict(tax_data[tax_id])
                            frete_report[tag_id][tax_id].update({"net": 0.0, "tax": 0.0})
                        else:
                            if tax_id not in frete_report[tag_id].keys():
                                frete_report[tag_id][tax_id] = dict(tax_data[tax_id])
                                frete_report[tag_id][tax_id].update(
                                    {"net": 0.0, "tax": 0.0}
                                )
                        frete_report[tag_id][tax_id]["net"] += tax_move_line["net"]
                        frete_report[tag_id][tax_id]["tax"] += tax_move_line["tax"]
                        frete_report[tag_id]["net"] += tax_move_line["net"]
                        frete_report[tag_id]["tax"] += tax_move_line["tax"]
        tags_data = self._get_tags_data(frete_report.keys())
        frete_report_list = []
        for tag_id in frete_report.keys():
            frete_report[tag_id]["name"] = tags_data[tag_id]["name"]
            frete_report[tag_id]["code"] = tags_data[tag_id]["code"]
            if tax_detail:
                frete_report[tag_id]["taxes"] = []
                for tax_id in frete_report[tag_id]:
                    if isinstance(tax_id, int):
                        frete_report[tag_id]["taxes"].append(frete_report[tag_id][tax_id])
            frete_report_list.append(frete_report[tag_id])
        return frete_report_list

    def _get_report_values(self, docids, data):
        # import pudb;pu.db
        res = super()._get_report_values(docids, data)
        wizard_id = data["wizard_id"]
        company = self.env["res.company"].browse(data["company_id"])
        company_id = data["company_id"]
        date_from = fields.Date.from_string(data["date_from"])
        date_to = fields.Date.from_string(data["date_to"])
        accounts_ids = data.get("account_ids", None)
        # based_on = data["based_on"]
        tax_detail = []
        # only_posted_moves = data["only_posted_moves"]
        frete_report_data, tax_data = self._get_frete_report_data(
            company_id, date_from, date_to, accounts_ids=accounts_ids
        )
        # if based_on == "taxgroups":
        #     vat_report = self._get_vat_report_group_data(
        #         vat_report_data, tax_data, tax_detail
        #     )
        # else:
        frete_report = self._get_frete_report_tag_data(
            frete_report_data, tax_data, tax_detail
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
                # "based_on": dict(
                #     self.env["vat.report.wizard"]
                #     ._fields["based_on"]
                #     ._description_selection(self.env)
                # ).get(data["based_on"]),
                "tax_detail": [],
                "frete_report": frete_report,
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
            "tax_ids",
            "tax_line_id",
            "move_id",
            "balance"
        ]
