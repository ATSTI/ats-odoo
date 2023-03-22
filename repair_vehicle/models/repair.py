# -*- coding: utf-8 -*-
# © 2018  Carlos R. Silveira
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from ast import literal_eval
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
        states={'draft': [('readonly', False)]})

    contas_pendentes = fields.Monetary('Faturas')

    currency_id = fields.Many2one(
        comodel_name="res.currency",
        default=lambda self: self.env.user.company_id.currency_id,
        store=True,
        readonly=True,
    )
    user_id = fields.Many2one(
        'res.users',
        string='Responsável',)
    
    sale_ids = fields.Many2one(
        'sale.order', 'Cotações',
        copy=False, track_visibility="onchange")

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

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        contas = self.env["account.move.line"].search([
            ('date_maturity', '<', fields.Date.today()),
            ('partner_id', '=', self.partner_id.id),
            ('reconciled', '=', False)
        ])
        valor = 0.0
        for ct in contas:
            valor += ct.amount_residual
        self.contas_pendentes = valor
        
    # @api.model
    # def _cliente_id_stage_ids(self):
    #     if self.cliente_id = "":
    #         raise ValidationError(
    #             _('Cliente Arquivado'))
    #     return

    def action_open_invoice(self):
        contas = self.env["account.move.line"].search([
            ('date_maturity', '<', fields.Date.today()),
            ('partner_id', '=', self.partner_id.id),
            ('reconciled', '=', False)
        ])
        domain = [("id", "in", contas.ids)]
        return {
            'name': 'Contas a receber',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'view_type': 'form',
            'res_model': 'account.move.line',
            'view_id': self.env.ref('br_account_payment.view_payments_tree_a_receber').id,
            'domain': domain,
        }

    def write(self, vals):
        if 'state' in vals:
            if vals['state'] == 'draft':
                vals['stage_id'] = 1
        res = super().write(vals)
        return res

    @api.multi
    def action_view_sale_order(self):
        quotations = self.mapped('sale_ids')
        action = self.env.ref('sale.action_orders').read()[0]
        if len(quotations) > 1:
            action['domain'] = [('id', 'in', quotations.ids)]
        elif len(quotations) == 1:
            form_view = [(self.env.ref('sale.view_order_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = quotations.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.multi
    def action_create_sale_order(self):
        vals={
            "name": self.name,
            "partner_id": self.partner_id.id,
        }
        sale = self.env["sale.order"].create(vals)
        self.sale_ids = sale.id        
    # return res
