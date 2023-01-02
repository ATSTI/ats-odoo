# Author: Damien Crier
# Author: Julien Coux
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class CashFlowReportWizard(models.TransientModel):
    """Open items report wizard."""

    _name = "cash.flow.report.wizard"
    _description = "Cash Flow Report Wizard"
    _inherit = "account_financial_report_abstract_wizard"

    date_at = fields.Date(string="Data final", required=True, default=fields.Date.context_today)
    date_from = fields.Date(string="Data inicio")
    target_move = fields.Selection(
        [("posted", "Todas entradas postadas"), ("all", "Todas Entradas")],
        string="Movimentos",
        required=True,
        default="posted",
    )
    account_ids = fields.Many2many(
        comodel_name="account.account",
        string="Filtro contas",
        domain=["|",("reconcile", "=", True), ("user_type_id", "=", 3)],
        required=True,
    )
    hide_account_at_0 = fields.Boolean(
        string="Ocultar saldo zerado",
        default=True,
        help="Use this filter to hide an account or a partner "
        "with an ending balance at 0. "
        "If partners are filtered, "
        "debits and credits totals will not match the trial balance.",
    )
    receivable_accounts_only = fields.Boolean()
    payable_accounts_only = fields.Boolean()
    partner_ids = fields.Many2many(
        comodel_name="res.partner",
        string="Filtro parceiros",
        default=lambda self: self._default_partners(),
    )
    foreign_currency = fields.Boolean(
        string="Mostrar moeda estrangeira",
        help="Display foreign currency for move lines, unless "
        "account currency is not setup through chart of accounts "
        "will display initial and final balance in that currency.",
        default=lambda self: self._default_foreign_currency(),
    )
    show_partner_details = fields.Boolean(
        string="Mostrar detalhe parceiros",
        default=False,
    )
    account_code_from = fields.Many2one(
        comodel_name="account.account",
        string="Conta inicial",
        help="Starting account in a range",
    )
    account_code_to = fields.Many2one(
        comodel_name="account.account",
        string="Conta final",
        help="Ending account in a range",
    )

    @api.onchange("account_code_from", "account_code_to")
    def on_change_account_range(self):
        if (
            self.account_code_from
            and self.account_code_from.code.isdigit()
            and self.account_code_to
            and self.account_code_to.code.isdigit()
        ):
            start_range = int(self.account_code_from.code)
            end_range = int(self.account_code_to.code)
            self.account_ids = self.env["account.account"].search(
                [
                    ("code", ">=", start_range),
                    ("code", "<=", end_range),
                    ("reconcile", "=", True),
                ]
            )
            if self.company_id:
                self.account_ids = self.account_ids.filtered(
                    lambda a: a.company_id == self.company_id
                )
        return {
            "domain": {
                "account_code_from": [("reconcile", "=", True)],
                "account_code_to": [("reconcile", "=", True)],
            }
        }

    def _default_foreign_currency(self):
        return self.env.user.has_group("base.group_multi_currency")

    @api.onchange("company_id")
    def onchange_company_id(self):
        """Handle company change."""
        if self.company_id and self.partner_ids:
            self.partner_ids = self.partner_ids.filtered(
                lambda p: p.company_id == self.company_id or not p.company_id
            )
        if self.company_id and self.account_ids:
            if self.receivable_accounts_only or self.payable_accounts_only:
                self.onchange_type_accounts_only()
            else:
                self.account_ids = self.account_ids.filtered(
                    lambda a: a.company_id == self.company_id
                )
        res = {"domain": {"account_ids": [], "partner_ids": []}}
        if not self.company_id:
            return res
        else:
            res["domain"]["account_ids"] += [("company_id", "=", self.company_id.id)]
            res["domain"]["partner_ids"] += self._get_partner_ids_domain()
        return res

    @api.onchange("account_ids")
    def onchange_account_ids(self):
        return {"domain": {"account_ids": ["|", ("reconcile", "=", True), ("user_type_id", "=", 3)]}}

    @api.onchange("receivable_accounts_only", "payable_accounts_only")
    def onchange_type_accounts_only(self):
        """Handle receivable/payable accounts only change."""
        domain = [("company_id", "=", self.company_id.id)]
        if self.receivable_accounts_only or self.payable_accounts_only:
            if self.receivable_accounts_only and self.payable_accounts_only:
                domain += [("internal_type", "in", ("receivable", "payable"))]
            elif self.receivable_accounts_only:
                domain += [("internal_type", "=", "receivable")]
            elif self.payable_accounts_only:
                domain += [("internal_type", "=", "payable")]
            self.account_ids = self.env["account.account"].search(domain)
        else:
            self.account_ids = None

    def _print_report(self, report_type):
        self.ensure_one()
        data = self._prepare_report_cash_flow()
        if report_type == "xlsx":
            report_name = "cash_flow_report.cash_flow_report_xlsx"
        else:
            report_name = "cash_flow_report.cash_flow_report"
        report = self.env["ir.actions.report"].search(
            [("report_name", "=", report_name), ("report_type", "=", report_type)],
            limit=1,
        )
        return (
            report.report_action(self, data=data)
        )

    def _prepare_report_cash_flow(self):
        self.ensure_one()
        return {
            "wizard_id": self.id,
            "date_at": fields.Date.to_string(self.date_at),
            "date_from": self.date_from or False,
            "only_posted_moves": self.target_move == "posted",
            "hide_account_at_0": self.hide_account_at_0,
            "foreign_currency": self.foreign_currency,
            "show_partner_details": self.show_partner_details,
            "company_id": self.company_id.id,
            "target_move": self.target_move,
            "account_ids": self.account_ids.ids,
            "partner_ids": self.partner_ids.ids or [],
            "account_financial_report_lang": self.env.lang,
        }

    def _export(self, report_type):
        return self._print_report(report_type)
