# Copyright (C) 2014  Renato Lima - Akretion
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, fields, models

ACCOUNT_DOMAIN = "['&', '&', '&', ('deprecated', '=', False), ('internal_type','=','other'), ('company_id', '=', current_company_id), ('is_off_balance', '=', False)]"

class Company(models.Model):
    _inherit = "res.company"

    property_account_income_freight_id = fields.Many2one(
        'account.account', company_dependent=True,
        string="Despesas vendas com Frete",
        domain=ACCOUNT_DOMAIN,
    )
    property_account_expense_freight_id = fields.Many2one(
        'account.account', company_dependent=True,
        string="Despesas com Frete",
        domain=ACCOUNT_DOMAIN,
    )

