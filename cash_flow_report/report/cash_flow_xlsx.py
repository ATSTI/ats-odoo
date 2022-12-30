# Author: Julien Coux
# Copyright 2016 Camptocamp SA
# Copyright 2021 Tecnativa - João Marques
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, models


class CashFlowReportXlsx(models.AbstractModel):
    _name = "report.cash_flow_report.cash_flow_report_xlsx"
    _description = "Cash Flow XLSX Report"
    _inherit = "report.cash_flow_report.abstract_report_xlsx"

    def _get_report_name(self, report, data=False):
        company_id = data.get("company_id", False)
        report_name = _("Fluxo de caixa")
        if company_id:
            company = self.env["res.company"].browse(company_id)
            suffix = " - {} - {}".format(company.name, company.currency_id.name)
            report_name = report_name + suffix
        return report_name

    def _get_report_columns(self, report):
        res = {
            0: {"header": _("Data"), "field": "date_maturity", "width": 11},
            1: {"header": _("Lançamento"), "field": "move_name", "width": 18},
            2: {"header": _("Conta"), "field": "account", "width": 9},
            3: {"header": _("Parceiro"), "field": "partner_name", "width": 25},
            4: {"header": _("Tipo"), "field": "payment", "width": 8},
            5: {"header": _("Ref - Descrição"), "field": "ref_label", "width": 40},
            6: {"header": _("Data emissao"), "field": "date", "width": 11},
            7: {
                "header": _("Receber"),
                "field": "debit",
                "field_final_balance": "debit",
                "type": "amount",
                "width": 14,
            },
            8: {
                "header": _("Pagar"),
                "field": "credit",
                "field_final_balance": "credit",
                "type": "amount",
                "width": 14,
            },
            9: {
                "header": _("Saldo"),
                "field": "balance",
                "field_final_balance": "balance",
                "type": "amount",
                "width": 14,
            },
        }
        if report.foreign_currency:
            foreign_currency = {
                10: {
                    "header": _("Cur."),
                    "field": "currency_name",
                    "field_currency_balance": "currency_name",
                    "type": "currency_name",
                    "width": 7,
                },
                11: {
                    "header": _("Cur. Original"),
                    "field": "amount_currency",
                    "field_final_balance": "amount_currency",
                    "type": "amount_currency",
                    "width": 14,
                },
                12: {
                    "header": _("Cur. Residual"),
                    "field": "amount_residual_currency",
                    "field_final_balance": "amount_currency",
                    "type": "amount_currency",
                    "width": 14,
                },
            }
            res = {**res, **foreign_currency}
        return res

    def _get_report_filters(self, report):
        return [
            [_("Date at filter"), report.date_at.strftime("%d/%m/%Y")],
            [
                _("Target moves filter"),
                _("All posted entries")
                if report.target_move == "posted"
                else _("All entries"),
            ],
            [
                _("Account balance at 0 filter"),
                _("Hide") if report.hide_account_at_0 else _("Show"),
            ],
            [
                _("Show foreign currency"),
                _("Yes") if report.foreign_currency else _("No"),
            ],
        ]

    def _get_col_count_filter_name(self):
        return 2

    def _get_col_count_filter_value(self):
        return 2

    def _get_col_count_final_balance_name(self):
        return 5

    def _get_col_pos_final_balance_label(self):
        return 5

    def _generate_report_content(self, workbook, report, data, report_data):
        res_data = self.env[
            "report.cash_flow_report.cash_flow_report"
        ]._get_report_values(report, data)
        # For each account
        Open_items = res_data["Open_Items"]
        accounts_data = res_data["accounts_data"]
        partners_data = res_data["partners_data"]
        journals_data = res_data["journals_data"]
        balance_list = res_data["balance_list"]
        balance = balance_list[0]['balance_value']
        total_amount = res_data["total_amount"]
        show_partner_details = res_data["show_partner_details"]
        for date_ocor in Open_items.keys():
            if Open_items[date_ocor]:
                # Open_items[account_id][0]['account_name'] 
                # Write account title
                self.write_array_title(
                    str(Open_items[date_ocor][0]['date_maturity']),
                    report_data,
                )

                # imprime o codigo da Conta no topo de cada data
                # for balance in balance_list:
                #     type_object = "balance"
                #     self.write_array_title(
                #         balance["account_id"], report_data
                #     )
                self.write_array_header(report_data)
            total_debit = 0.0
            total_credit = 0.0
            if Open_items[date_ocor]:
                if Open_items[date_ocor]:
                    # Display array header for move lines

                    # Display account move lines
                    for line in Open_items[date_ocor]:
                        if line['debit']:
                            balance += line['debit']
                            total_debit += line['debit']
                        if line['credit']:
                            balance -= line['credit']
                            total_credit += line['credit']
                        line.update(
                            {
                                "account": line['account_name'],
                                "journal": journals_data[line["journal_id"]]["code"],
                                "balance": balance,
                            }
                        )
                        self.write_line_from_dict(line, report_data)
                # balance -= total_amount[date_ocor]["residual"]

                # Display ending balance line for account
                type_object = "account"
                self.write_ending_balance_from_dict(
                    accounts_data,
                    type_object,
                    total_amount,
                    total_debit,
                    total_credit,
                    report_data,
                    account_id=Open_items[date_ocor][0]['account_id'],
                    date_ocor=date_ocor,
                    balance_list=balance,
                )
                type_object = "balance"
                self.write_ending_balance_from_dict(
                    accounts_data,
                    type_object,
                    total_amount,
                    total_debit,
                    total_credit,
                    report_data,
                    account_id=Open_items[date_ocor][0]['account_id'],
                    date_ocor=date_ocor,
                    balance_list=balance,
                )
                # 2 lines break
                report_data["row_pos"] += 2

                # imprime o saldo acumulado


    def write_ending_balance_from_dict(
        self,
        my_object,
        type_object,
        total_amount,
        total_debit,
        total_credit,
        report_data,
        account_id=False,
        partner_id=False,
        date_ocor=False,
        balance_list=False,
    ):
        """Specific function to write ending balance for Open Items"""
        if type_object == "partner":
            name = my_object["name"]
            my_object["residual"] = total_amount[account_id][partner_id]["residual"]
            label = _("Partner ending balance")
        elif type_object == "account":
            name = account_id[0]
            my_object["credit"] = total_credit
            my_object["debit"] = total_debit
            label = _("Ending balance")
        elif type_object == "balance":
            name = account_id[0]
            my_object["balance"] = balance_list
            label = _("Total acumulado")
        if type_object in ("partner", "balance"):
            super(CashFlowReportXlsx, self).write_ending_balance_from_dict(
                my_object, name, label, report_data
            )

    def _write_filters(self, filters, report_data, objects, data):
        res_data = self.env[
            "report.cash_flow_report.cash_flow_report"
        ]._get_report_values(objects, data)
        balance_list = res_data["balance_list"]        
        # For each account
        col_name = 1
        res = super(CashFlowReportXlsx, self)._write_filters(
            filters, report_data
        )
        balance_start = "%s - %s" %(balance_list[0]['bank'], str(balance_list[0]['balance_value']))
        report_data["sheet"].merge_range(
                report_data["row_pos"],
                col_name,
                report_data["row_pos"],
                col_name + 3,
                balance_start,
                report_data["formats"]["format_header_left"],
            )
        report_data["row_pos"] += 1

        return res

    def generate_xlsx_report(self, workbook, data, objects):
        # Initialize report variables
        report_data = {
            "workbook": None,
            "sheet": None,  # main sheet which will contains report
            "columns": None,  # columns of the report
            "row_pos": None,  # row_pos must be incremented at each writing lines
            "formats": None,
        }
        self._define_formats(workbook, report_data)
        # Get report data
        report_name = self._get_report_name(objects, data=data)
        report_footer = self._get_report_footer()
        filters = self._get_report_filters(objects)
        report_data["columns"] = self._get_report_columns(objects)
        report_data["workbook"] = workbook
        report_data["sheet"] = workbook.add_worksheet(report_name[:31])
        self._set_column_width(report_data)
        # Fill report
        report_data["row_pos"] = 0
        self._write_report_title(report_name, report_data)
        self._write_filters(filters, report_data, objects, data)
        self._generate_report_content(workbook, objects, data, report_data)
        self._write_report_footer(report_footer, report_data)