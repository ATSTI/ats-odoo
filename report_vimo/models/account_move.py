# -*- coding: utf-8 -*-
from odoo import fields, models, _, api
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta, date

class AccountMove(models.Model):
    _inherit = "account.move"

    def get_payment_date(self):
        self.ensure_one()
        for rec in self.line_ids:
            if rec.full_reconcile_id:
                # pega a primeira linha conciliada com data
                for reconciled_line in rec.full_reconcile_id.reconciled_line_ids:
                    if reconciled_line.date:
                        return reconciled_line.date.strftime('%d/%m/%y') #achei este metodo, e segundo pesquisas, ele se linka com a data das faturas reconciliadas(pagas)
        return False
