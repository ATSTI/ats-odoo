from odoo import models, fields, api
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def create(self, vals):
        res = super().create(vals)
        msg = """Não verificamos o seu pagamento.
        Por favor, contate o financeiro, whatsapp: 1997104-0941

        SEU SISTEMA ESTÁ BLOQUEADO!!!
        """

        if (
            self.env.user.payment_pending
            and "BLOQUEADO!!!" in (self.env.user.mensage_pai or "")
        ):
            raise UserError(msg)
        else:
            return res



   