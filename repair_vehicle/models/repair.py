# -*- coding: utf-8 -*-
# © 2018  Carlos R. Silveira
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError


class Repair(models.Model):
    _inherit = 'repair.order'

    def _default_stage_id(self):
        stage_ids = self.env['repair.stage'].\
            search([('stage_type', '=', 'order'),
                    ('is_default', '=', True),
                    ('company_id', 'in', (self.env.user.company_id.id,
                                          False))],
                   order='sequence asc', limit=1)
        if stage_ids:
            return stage_ids[0]
        else:
            raise ValidationError(_(
                "You must create an FSM order stage first."))
    
    stage_id = fields.Many2one('repair.stage', string='Stage',
            track_visibility='onchange',
            index=True, copy=False,
            group_expand='_read_group_stage_ids',
            default=lambda self: self._default_stage_id())
    vehicle_id = fields.Many2one(
        'repair.vehicle', string='Veículo',
        required=True, states={'draft': [('readonly', False)]})

    cliente_id = fields.Many2one(
        'res.partner', 'Cliente',
        index=True, states={'confirmed': [('readonly', True)]}, check_company=True, change_default=True,
        )

    contas_pendentes = fields.Char('Contas')

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        search_domain = [('stage_type', '=', 'order')]
        if self.env.context.get('default_team_id'):
            search_domain = [
                '&', ('team_ids', 'in', self.env.context['default_team_id'])
            ] + search_domain
        return stages.search(search_domain, order=order)

    @api.onchange('vehicle_id')
    def onchange_vehicle_id(self):
        prod_id = self.env["product.product"].search([('type', 'in', ['product', 'consu'])], limit=1)
        self.product_id = prod_id.id
        self.product_uom = prod_id.uom_id.id

    @api.onchange('cliente_id')
    def onchange_cliente_id(self):
        contas = self.env["account.move.line"].search([('date_maturity', '<', fields.Date.today()), ('partner_id', '=', self.cliente_id.id)])
        # fatura = ""
        # for ct in contas:
        #     fatura += ct.name + ", "
        self.contas_pendentes = contas.ids 
        
    # @api.model
    # def _cliente_id_stage_ids(self):
    #     if self.cliente_id = "":
    #         raise ValidationError(
    #             _('Cliente Arquivado'))
    #     return

    def action_open_invoice(self):
        contas = self.env["account.move.line"].search([('date_maturity', '<', fields.Date.today()), ('partner_id', '=', self.cliente_id.id)])
        domain = [("id", "in", contas.ids)]
        return {
            'name': 'CA par adhérent',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'view_type': 'form',
            'res_model': 'account.move.line',
            'view_id': self.env.ref('br_account_payment.view_payments_tree_a_receber').id,
            'domain': domain,
        }