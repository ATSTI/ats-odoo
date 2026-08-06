# Copyright 2020 ATS Solucoes (https://atsti.com.br)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from pytz import timezone
from odoo.exceptions import UserError


class ControleVisita(models.Model):
    _name = 'controle.visita'
    _description = 'Controle Visita'

    name = fields.Char('Nome Visitante', required=True)
    socio_id = fields.Many2one('res.partner', string="Socio", required=True)
    carteirinha = fields.Char('Carteirinha')
    data_visita = fields.Datetime(string="Data Visita", default=fields.Datetime.now)
    user_id = fields.Many2one('res.users', string='Usuário', index=True,
        track_visibility='onchange', track_sequence=2, default=lambda self: self.env.user)
    cobrado = fields.Boolean(string='Cobrado')

    @api.onchange('carteirinha')
    def _onchange_carteirinha(self):
        if self.carteirinha:
            prt = self.env['res.partner'].search([
                ('chave_acesso','=', self.carteirinha)
                ])
            if not prt:
                raise UserError(_('Carteirinha inválida.'))
            if prt.categoria not in ('1','2'):
                raise UserError(_('Sócio sem permissão para Convidado.'))
            self.socio_id = prt.id

    @api.onchange('socio_id')
    def _onchange_socio_id(self):
        if self.socio_id:
            if self.socio_id.categoria not in ('1','2'):
                raise UserError(_('Sócio sem permissão para Convidado.'))
            self.carteirinha = self.socio_id.chave_acesso

    def gerar_venda(self, partner, user, visitas):
        order_line = []
        vals = {}
        vals['client_order_ref'] = visitas
        #vals['date_order'] = datetime.strftime(
        #    datetime.now(),'%Y-%m-%d %H:%M:%S') + timedelta(hours=-3)
        vals['partner_id'] = partner.id
        vals['partner_invoice_id'] = partner.id
        vals['partner_shipping_id'] = partner.id
        vals['user_id'] = user.id
        vals['fiscal_position_id'] = 1
        vals['payment_term_id'] = 1
        vals['name'] = 'Visita %s' %(
            fields.Datetime.to_string(datetime.now() + timedelta(hours=-3)))
        prd = {}
        #prod_id = self.env['product.product'].search([
        #    ('default_code', '=', 'visita')], limit=1)
        prod_id = self.env['product.product'].browse([117])
        prd['product_id'] = prod_id.id
        prd['product_uom_qty'] = 1
        prd['product_uom'] = prod_id.uom_id.id
        prd['price_unit'] = prod_id.list_price
        prd['name'] = visitas
        order_line.append((0, 0,prd))
        vals['order_line']= order_line
        vnd = self.env['sale.order'].create(vals)
        vnd.action_confirm()

    @api.model
    def create(self, values):
        result = super(ControleVisita, self).create(values)
        # 05/08/2026 clube solicitou que seja ANUAL o numero 
        # de visitas, e não mensal.
        # O plano familiar tem 10 visitas por ano,
        # e o plano individual tem 5 visitas por ano
        mes_ini = '%s/01/01 00:00:00' %(
            result.data_visita.year,
        )
        #    str(result.data_visita.month).zfill(2)
        #    )
        # dia = 30
        # if result.data_visita.month == 2:
        #     dia = 28
        # if result.data_visita.month in (1,3,5,7,8,10,12):
        #     dia = 31
        mes_fim = '%s/12/31 21:59:00' %(
           result.data_visita.year
        )
        #    str(result.data_visita.month).zfill(2),
        #    str(dia))
        visita_ids = self.env['controle.visita'].search([
                ('socio_id','=', result.socio_id.id),
                ('data_visita', '>', mes_ini),
                ('data_visita', '<', mes_fim),
                ])
        num_visita = 10
        if result.socio_id.categoria == '2':
            num_visita = 5
        if len(visita_ids) > num_visita:
            visitas = 'Convidado : %s' %(result.name)
            self.gerar_venda(result.socio_id,
                result.user_id, visitas)
            result['cobrado'] = True
        return result
