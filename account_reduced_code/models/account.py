# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp


class AccountAccount(models.Model):
    _inherit = 'account.account'
    
    code_reduced = fields.Char(size=64, string="Cód. Reduzido")
