# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp


class AccountMove(models.Model):
    _inherit = 'account.move'


    def _write(self, vals):
        if self.partner_id.vat:
            if self.origin and self.partner_id.vat not in (self.origin):
                vals['origin'] = self.origin + ' - ' + self.partner_id.vat
            elif self.partner_id.vat not in (self.origin):
                vals['origin'] = self.partner_id.vat
        res = super(AccountMove, self)._write(vals)    
        return res
