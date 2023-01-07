# © 2021 Carlos R. Silveira <crsilveira@gmail.com>, ATSTi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models, _



class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def invoice_validate(self):
        res = super(AccountInvoice, self).invoice_validate()
        nf = 0
        if self.invoice_eletronic_ids:
            for nf in self.invoice_eletronic_ids:
                nf = nf.numero
        for rec in self.receivable_move_line_ids:
            if nf:
                if str(nf) not in rec.name:
                    nota = 'NF-%s(%s)' %(str(nf), rec.name)
                    rec.write({'name': nota})
        return res