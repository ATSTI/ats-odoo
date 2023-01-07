# See LICENSE file for full copyright and licensing details.


from odoo import api, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def check_limit(self):
        self.ensure_one()
        partner = self.partner_id
        if self.payment_term_id.id == 1:
            return True
        user_id = self.env['res.users'].search([
            ('partner_id', '=', partner.id)], limit=1)
        if user_id and not user_id.has_group('base.group_portal') or not \
                user_id:
            invoice_obj = self.env['account.invoice']
            invoicelines = invoice_obj.search(
                [('partner_id', '=', partner.id),
                 ('state', '=', 'open'),
                 ('residual', '>', 0)]
            )
            debit = 0.0
            for line in invoicelines:
                debit += line.residual
            partner_credit_limit = partner.credit_limit - debit
            if self.amount_total > partner_credit_limit:
                if not partner.over_credit:
                    msg = '{:,.2f}'.format(partner_credit_limit).replace(',','x')
                    msg = msg.replace('.',',').replace('x','.')
                    msg = 'O limite de crédito disponível é R$ %s.' % (msg)
                    raise UserError(_('Esta venda não pode ser confirmada \n'
                                      + msg))
                partner.write(
                    {'credit_limit': credit - debit + self.amount_total})
            return True

    @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            order.check_limit()
        return res

    @api.constrains('amount_total')
    def check_amount(self):
        for order in self:
            order.check_limit()
