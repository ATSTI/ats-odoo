# -*- coding: utf-8 -*-

from odoo import fields, models, _, api
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta, date

class AccountMove(models.Model):
    _inherit = "account.move"

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        res = super(AccountMove, self)._onchange_partner_id()
        self.narration = 'Data de Coleta: .......... / /2025 - 00:00\nData de Retirada: ....... / /2025 - 00:00'
        return res
  
    def get_payment_date(self):
        self.ensure_one()
        for rec in self.line_ids:
            if rec.full_reconcile_id:
                # pega a primeira linha conciliada com data
                for reconciled_line in rec.full_reconcile_id.reconciled_line_ids:
                    if reconciled_line.date:
                        return reconciled_line.date.strftime('%d/%m/%y') #achei este metodo, e segundo pesquisas, ele se linka com a data das faturas reconciliadas(pagas)
        return False

# tentei isto aqui pois eu vi no metodo account.move que existe o campo date_maturity, porem nao exibiu nada
    # def get_payment_date(self):
    #     self.ensure_one() #uma fatura por vez apenas
    #     for line in self.line_ids:
    #         if hasattr(line, 'payment_id') and line.payment_id:
    #             return line.payment_id.date_maturity
        
    #     return False