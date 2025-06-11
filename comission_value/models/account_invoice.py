# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Faslu Rahman(odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class AccountMove(models.Model):
    _inherit = "account.move"

    commission_value = fields.Float('Comissão', digits=dp.get_precision('Account'),
                                readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})

    @api.onchange('commission_value')
    def _onchange_comission_value(self):
        for move in self:
            if move.commission_value:
                value = move.commission_value - move.amount_price_gross
                value_percent = (value * 100 / move.amount_price_gross) * -1
                # self.amount_tax = value
                move.update({
                    'amount_tax': value,
                })
                for line in move.invoice_line_ids:
                    line.ipi_percent = value_percent
                    line.ipi_value = value
                move.amount_total = move.amount_price_gross + move.amount_tax
                move.amount_financial_total = move.amount_price_gross + move.amount_tax
                # move._amount_all()

    # def _prepare_invoice(self, ):
    #     return True
    #     invoice_vals = super(SaleOrder, self)._prepare_invoice()
    #     invoice_vals.update({
    #         'comission_type': self.comission_type,
    #         'comission_rate': self.comission_rate_t,
    #     })
    #     return invoice_vals

    def button_dummy(self): 
        self._onchange_comission_value()
        return True
