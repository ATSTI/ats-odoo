# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.model
    def create(self, vals):
        # Carlos 22/11/2021 , gravo no campo Name o número da nota fiscal e da parcela,
        # pra exibir em relatorio para a contabilidade
        if 'invoice_id' in vals and vals['invoice_id']:
            inv = self.env['account.invoice'].browse([vals['invoice_id']])
            if inv:
                if inv.nfe_number_static:
                    if len(vals['name']) == 2:
                        vals['name'] = 'NF-%s(%s)' %(str(inv.nfe_number_static), vals['name'])
                    else:
                        vals['name'] = vals['name'] + ' ' + str(inv.nfe_number_static)
        elif 'payment_id' in vals:
            payment = self.env['account.payment'].browse([vals['payment_id']])
            aml = self.env['account.move.line'].search([
                ('ref', '=', payment.communication),
                ('amount_residual', '>', 0.0),
                ('reconciled', '=', False),
                ('invoice_id', '!=', False)], order="id", limit=1)
            if aml:
                if str(aml.invoice_id.nfe_number_static) not in vals['name']:
                    vals['name'] = vals['name'] + ' - ' + aml.name
                if aml.name not in vals:
                    vals['name'] = vals['name'] + ' - ' + aml.name
            else:
                if vals['name'] not in payment.communication:
                    vals['name'] = vals['name'] + ' - ' + payment.communication
                else:
                    vals['name'] = payment.communication
                if str(aml.invoice_id.nfe_number_static) not in payment.communication:
                    payment.communication = vals['name']

        return super(AccountMoveLine, self).create(vals)
