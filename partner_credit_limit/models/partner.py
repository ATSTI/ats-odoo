# See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    over_credit = fields.Boolean('Permite venda acima limite?')
    
    
    @api.multi                                                                                                                                            
    def write(self, vals):
        if 'credit_limit' in vals or 'over_credit' in vals:
            #gerente = self.env['res.groups'].search([('name','=','group_sale_manager')])
            gerente = self.env.ref('sales_team.group_sale_manager')
            gerente = self._uid in gerente.users.ids
            if gerente:
                super(ResPartner, self).write(vals)
            else:
                raise UserError(_("Usuário não tem permissão  \
                               para alterar o limite de crédito."))
        else:
            super(ResPartner, self).write(vals)
