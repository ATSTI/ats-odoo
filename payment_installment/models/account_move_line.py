# -*- coding: utf-8 -*- © 2017 Carlos R. Silveira, ATSti
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.multi
    def action_payment_prc(self):
        compose_form = self.env.ref('view_installment_form', False)
        return {
            'view_mode': 'form',
            'view_id': compose_form,
            'res_model': 'payment.installment',
            'context': "{'type':'out_invoice'}",
            'type': 'ir.actions.act_window',
            'res_id': self.move_id.id,
        }
