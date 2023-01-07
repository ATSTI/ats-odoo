# -*- coding: utf-8 -*- © 2017 Carlos R. Silveira, ATSti
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _


class PaymentInstallment(models.TransientModel):
    _name = 'payment.installment'

    name = fields.Integer('Id Parcela')
    num_parcela = fields.Char('Número Parcela')
    data_vencimento = fields.Date('Data Vencimento')
    valor_parcela = fields.Float('Valor Parcela')

    @api.multi
    def action_payment_installment(self):
        rec = super(TransientModelClass, self).default_get(fields)
        for prc in self.move_id.line_ids:
             rec['name'] = prc.id
             rec['num_parcela'] = prc.name
             rec['data_vencimento'] = prc.date_maturity
             rec['valor_parcela'] = prc.amount_residual
             
        compose_form = self.env.ref('view_installment_form', False)
        return {
            'view_mode': 'form',
            'view_id': compose_form,
            'res_model': 'payment.installment',
            'context': "{'type':'out_invoice'}",
            'type': 'ir.actions.act_window',
            'res_id': rec,
        }
