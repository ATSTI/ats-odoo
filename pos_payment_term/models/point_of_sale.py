# -*- coding: utf-8 -*-
# © 2016 KMEE INFORMATICA LTDA (<http://kmee.com.br>).
#   Luiz Felipe do Divino <luiz.divino@kmee.com.br>
#   Luis Felipe Mileo <mileo@kmee.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def _payment_fields(self, ui_paymentline):

        result = super(PosOrder, self)._payment_fields(
            ui_paymentline
        )
        #teste
        journal_id = self.env['account.journal'].browse(ui_paymentline.get('journal_id'))
        for l in journal_id.payment_term_ids:
            if l:
                result['payment_term_id'] = l.id
            break
        #result['payment_term'] = ui_paymentline.get('payment_term', False)
        return result

    def add_payment(self, data):

        if data.get('payment_term_id'):
            payment_terms = self.env['account.payment.term'].browse(int(data['payment_term_id']))
            date_payment = data['payment_date'].split(" ")
            compute = payment_terms.compute(
                data['amount'],
                date_payment[0]
            )
            result = []
            amount = []
            payment_date = []
            for item in compute:
                for i in item:
                    #amount.append(i[1])
                    #payment_date.append(i[0])
                    data['payment_date'] = i[0]
                    data['amount'] = i[1]
                    result.append(
                        super(PosOrder, self).add_payment(
                            data
                        )
                    )
            return result

        return super(PosOrder, self).add_payment(
            data
        )
