# -*- coding: utf-8 -*-
from odoo import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _get_or_create_cpf_partner(self, cpf):
        import pudb;pudb.set_trace()
        cpf_limpo = ''.join(filter(str.isdigit, cpf))
        if len(cpf_limpo) != 11:
            return False
        partner = self.env['res.partner'].search(
            [('vat', '=', cpf_limpo)], limit=1
        )
        if not partner:
            partner = self.env['res.partner'].create({
                'name': f'Consumidor CPF {cpf_limpo}',
                'vat': cpf_limpo,
                'country_id': self.env.ref('base.br').id,
            })
        return partner