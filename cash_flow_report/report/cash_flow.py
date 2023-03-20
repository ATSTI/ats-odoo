# © 2016 Julien Coux (Camptocamp)
# Copyright 2020 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import operator
from datetime import date, datetime

from odoo import api, models
from odoo.tools import float_is_zero


class CashFlowReport(models.AbstractModel):
    _name = "report.cash_flow_report.cash_flow_report"
    _description = "Cash Flow Report"
    _inherit = "report.cash_flow_report.abstract_report"

    def _get_account_partial_reconciled(self, company_id, date_at_object):
        domain = [("max_date", ">", date_at_object), ("company_id", "=", company_id)]
        fields = ["debit_move_id", "credit_move_id", "amount"]
        accounts_partial_reconcile = self.env["account.partial.reconcile"].search_read(
            domain=domain, fields=fields
        )
        debit_amount = {}
        credit_amount = {}
        for account_partial_reconcile_data in accounts_partial_reconcile:
            debit_move_id = account_partial_reconcile_data["debit_move_id"][0]
            credit_move_id = account_partial_reconcile_data["credit_move_id"][0]
            if debit_move_id not in debit_amount.keys():
                debit_amount[debit_move_id] = 0.0
            debit_amount[debit_move_id] += account_partial_reconcile_data["amount"]
            if credit_move_id not in credit_amount.keys():
                credit_amount[credit_move_id] = 0.0
            credit_amount[credit_move_id] += account_partial_reconcile_data["amount"]
            account_partial_reconcile_data.update(
                {"debit_move_id": debit_move_id, "credit_move_id": credit_move_id}
            )
        return accounts_partial_reconcile, debit_amount, credit_amount

    def _get_data(
        self,
        account_ids,
        partner_ids,
        date_at_object,
        only_posted_moves,
        company_id,
        date_from,
        tipo,
    ):

        # como carregar este cara duas vezes ... com tipo == liquidity

        domain = self._get_move_lines_domain_not_reconciled(
            company_id, account_ids, partner_ids, only_posted_moves, date_from, tipo
        )
        ml_fields = [
            "id",
            "name",
            "date",
            "move_id",
            "journal_id",
            "account_id",
            "partner_id",
            "payment_mode_id",
            "amount_residual",
            "date_maturity",
            "ref",
            "debit",
            "credit",
            "reconciled",
            "currency_id",
            "amount_currency",
            "amount_residual_currency",
            "balance",
        ]
        move_lines = self.env["account.move.line"].search_read(
            domain=domain, fields=ml_fields, order="date_maturity"
        )
        journals_ids = set()
        partners_ids = set()
        partners_data = {}
        if date_at_object < date.today():
            (
                acc_partial_rec,
                debit_amount,
                credit_amount,
            ) = self._get_account_partial_reconciled(company_id, date_at_object)
            if acc_partial_rec:
                ml_ids = list(map(operator.itemgetter("id"), move_lines))
                debit_ids = list(
                    map(operator.itemgetter("debit_move_id"), acc_partial_rec)
                )
                credit_ids = list(
                    map(operator.itemgetter("credit_move_id"), acc_partial_rec)
                )
                move_lines = self._recalculate_move_lines(
                    move_lines,
                    debit_ids,
                    credit_ids,
                    debit_amount,
                    credit_amount,
                    ml_ids,
                    account_ids,
                    company_id,
                    partner_ids,
                    only_posted_moves,
                )
        move_lines = [
            move_line
            for move_line in move_lines
            if move_line["date_maturity"] <= date_at_object
            and not float_is_zero(move_line["amount_residual"], precision_digits=2)
        ]

        open_items_move_lines_data = {}
        balance = 0
        contas_key = []
        for move_line in move_lines:
            journals_ids.add(move_line["journal_id"][0])
            contas_key.append(move_line["account_id"][0])
            if move_line["date_maturity"]:
                dt_time = move_line["date_maturity"]
            else:
                dt_time = move_line["date"]
            date_vcto = 10000*dt_time.year + 100*dt_time.month + dt_time.day
            acc_id = date_vcto
            # Partners data
            if move_line["partner_id"]:
                prt_id = move_line["partner_id"][0]
                prt_name = move_line["partner_id"][1]
            else:
                # TODO se for banco, pegar Conta e Agencia
                prt_id = 0
                prt_name = "Missing Partner"
            if prt_id not in partners_ids:
                partners_data.update({prt_id: {"id": prt_id, "name": prt_name}})
                partners_ids.add(prt_id)

            # Move line update
            original = 0

            if not float_is_zero(move_line["credit"], precision_digits=2):
                original = move_line["credit"] * (-1)
                balance += move_line["credit"]
            if not float_is_zero(move_line["debit"], precision_digits=2):
                original = move_line["debit"]
                balance += move_line["debit"]

            if move_line["ref"] == move_line["name"]:
                if move_line["ref"]:
                    ref_label = move_line["ref"]
                else:
                    ref_label = ""
            elif not move_line["ref"]:
                ref_label = move_line["name"]
            elif not move_line["name"]:
                ref_label = move_line["ref"]
            else:
                ref_label = move_line["ref"] + str(" - ") + move_line["name"]
            account_name = ""
            if move_line["account_id"]:
                account_name = move_line["account_id"][1]
            # move_id = self.env["account.move"].browse([move_line["move_id"][0]])
            # if move_id.ref:
            #     if ref_label:
            #         ref_label += ', ' + move_id.ref
            #     else:
            #         ref_label = move_id.ref
            # payment_mode = move_id.payment_mode_id.name
            payment_mode = ""
            payment_mode_id = 0
            if move_line["payment_mode_id"]:
                payment_mode = move_line["payment_mode_id"][1]
                payment_mode_id = move_line["payment_mode_id"][0]
            move_line.update(
                {
                    "date": move_line["date"],
                    "date_maturity": move_line["date_maturity"]
                    and move_line["date_maturity"].strftime("%d/%m/%Y"),
                    "original": original,
                    "partner_id": prt_id,
                    "partner_name": prt_name,
                    "payment_mode_id": payment_mode_id,
                    "payment_mode_name": payment_mode,
                    "account_name": account_name,
                    "ref_label": ref_label,
                    "journal_id": move_line["journal_id"][0],
                    "move_name": move_line["move_id"][1],
                    "entry_id": move_line["move_id"][0],
                    "currency_id": move_line["currency_id"][0]
                    if move_line["currency_id"]
                    else False,
                    "currency_name": move_line["currency_id"][1]
                    if move_line["currency_id"]
                    else False,
                    "amount_balance": balance,
                }
            )

            # Open Items Move Lines Data
            # if acc_id not in open_items_move_lines_data.keys():
            #     open_items_move_lines_data[acc_id] = {prt_id: [move_line]}
            # else:
            #     if prt_id not in open_items_move_lines_data[acc_id].keys():
            #         open_items_move_lines_data[acc_id][prt_id] = [move_line]
            #     else:
            #         open_items_move_lines_data[acc_id][prt_id].append(move_line)
            if acc_id not in open_items_move_lines_data.keys():
                open_items_move_lines_data[acc_id] = {prt_id: [move_line]}
            else:
                if prt_id not in open_items_move_lines_data[acc_id].keys():
                    open_items_move_lines_data[acc_id][prt_id] = [move_line]
                else:
                    open_items_move_lines_data[acc_id][prt_id].append(move_line)
        journals_data = self._get_journals_data(list(journals_ids))
        # accounts_data = self._get_accounts_data(open_items_move_lines_data.keys())
        accounts_data = self._get_accounts_data(contas_key)
        return (
            move_lines,
            partners_data,
            journals_data,
            accounts_data,
            open_items_move_lines_data,
        )

    @api.model
    def _calculate_amounts(self, open_items_move_lines_data):
        total_amount = {}
        total_amount["balance"] = 0.0
        for account_id in open_items_move_lines_data.keys():
            total_amount[account_id] = {}
            total_amount[account_id]["residual"] = 0.0
            for partner_id in open_items_move_lines_data[account_id].keys():
                total_amount[account_id][partner_id] = {}
                total_amount[account_id][partner_id]["residual"] = 0.0
                for move_line in open_items_move_lines_data[account_id][partner_id]:
                    total_amount[account_id][partner_id]["residual"] += move_line[
                        "amount_residual"
                    ]
                    total_amount[account_id]["residual"] += move_line["amount_residual"]
                total_amount["balance"] += move_line["amount_residual"]
        return total_amount

    @api.model
    def _order_open_items_by_date(
        self, open_items_move_lines_data, show_partner_details, partners_data, tipo
    ):
        new_open_items = {}
        if not show_partner_details:
            for acc_id in open_items_move_lines_data.keys():
                new_open_items[acc_id] = {}
                move_lines = []
                for prt_id in open_items_move_lines_data[acc_id]:
                    for move_line in open_items_move_lines_data[acc_id][prt_id]:
                        move_lines += [move_line]
                # if tipo == "liquidity":
                move_lines = sorted(move_lines, key=lambda k: (k["date"]))
                # else:
                    # move_lines = sorted(move_lines, key=lambda k: (k["date_maturity"]))
                new_open_items[acc_id] = move_lines
        else:
            for acc_id in open_items_move_lines_data.keys():
                new_open_items[acc_id] = {}
                for prt_id in sorted(
                    open_items_move_lines_data[acc_id],
                    key=lambda i: partners_data[i]["name"],
                ):
                    new_open_items[acc_id][prt_id] = {}
                    move_lines = []
                    for move_line in open_items_move_lines_data[acc_id][prt_id]:
                        move_lines += [move_line]
                    # if tipo == "liquidity":
                    move_lines = sorted(move_lines, key=lambda k: (k["date"]))
                    # else:
                        # move_lines = sorted(move_lines, key=lambda k: (k["date_maturity"]))

                    new_open_items[acc_id][prt_id] = move_lines
        return new_open_items

    def _get_report_values(self, docids, data):
        wizard_id = data["wizard_id"]
        company = self.env["res.company"].browse(data["company_id"])
        company_id = data["company_id"]
        account_ids = data["account_ids"]
        partner_ids = data["partner_ids"]
        date_at = data["date_at"]
        date_at_object = datetime.strptime(date_at, "%Y-%m-%d").date()
        date_from = data["date_from"]
        date_from_object = date_at_object
        if date_from:
            date_from_object =  datetime.strptime(date_from, "%Y-%m-%d").date()
        only_posted_moves = data["only_posted_moves"]
        show_partner_details = data["show_partner_details"]
        
        # contas bancarias e caixa
        account_bank = self.env["account.account"].search([
            ("id", "in", account_ids),
            ("internal_type", "=", "liquidity"),
        ])
        copy_account_ids = account_ids
        # Removo as contas Caixa e Banco
        acc_ids = account_ids
        # for acc in account_bank.ids:
        #     acc_ids.remove(acc)
        tipo = "outros"
        (
            move_lines_data,
            partners_data,
            journals_data,
            accounts_data,
            open_items_move_lines_data,
        ) = self._get_data(
            acc_ids,
            partner_ids,
            date_at_object,
            only_posted_moves,
            company_id,
            date_from_object,
            tipo,
        )

        total_amount = self._calculate_amounts(open_items_move_lines_data)
        open_items_move_lines_data = self._order_open_items_by_date(
            open_items_move_lines_data, show_partner_details, partners_data, tipo
        )

        balance_values = self.env["account.move.line"].read_group([
                ("account_id", "in", account_bank.ids),
                ("date", "<=", data["date_from"])
            ], #domain
            ["account_id", "balance:sum"], #fields
            ["account_id"] #group_by
        )
        balance_list = []
        for balance in balance_values:
            vals = {
                'account_id': balance['account_id'][0],
                'bank': balance['account_id'][1],
                'balance_value': balance['balance']
            }
            balance_list.append(vals)

        return {
            "doc_ids": [wizard_id],
            "doc_model": "cash.flow.report.wizard",
            "docs": self.env["cash.flow.report.wizard"].browse(wizard_id),
            "foreign_currency": data["foreign_currency"],
            "show_partner_details": data["show_partner_details"],
            "company_name": company.display_name,
            "currency_name": company.currency_id.name,
            "date_at": date_at_object.strftime("%d/%m/%Y"),
            "date_from": date_from_object.strftime("%d/%m/%Y"),
            "hide_account_at_0": data["hide_account_at_0"],
            "target_move": data["target_move"],
            "journals_data": journals_data,
            "partners_data": partners_data,
            "accounts_data": accounts_data,
            "total_amount": total_amount,
            "Open_Items": open_items_move_lines_data,
            "balance_start": balance_values,
            "balance_list": balance_list,
        }
