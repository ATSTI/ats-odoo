# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from datetime import date


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    imovel_id = fields.Many2one(
        'imovel',
        string='Imovel',
        required=True
        )
        
    @api.onchange('imovel_id')
    def onchange_imovel_id(self):
        if self.imovel_id:
            self.name = self.imovel_id.name
            today = date.today()
            self.code = '%s-%s-%s' %(
                self.imovel_id.name, 
                str(today.month).zfill(2),
                str(today.year)
                )
        return {}
        
    @api.model
    def _prepare_invoice(self):
        invoice_vals = super(AccountAnalyticAccount, self).\
            _prepare_invoice()
        if self.payment_mode_id:
            invoice_vals['payment_mode_id'] = self.payment_mode_id.id
            #invoice_vals['partner_bank_id'] = (
            #    contract.partner_id.bank_ids[:1].id or
            #    contract.payment_mode_id.bank_id.id)
        if self.payment_term_id:
            invoice_vals['payment_term_id'] = self.payment_term_id.id
        if self.fiscal_position_id:
            invoice_vals['fiscal_position_id'] = self.fiscal_position_id.id
        invoice_vals['contract_id'] = self.id
        today = date.today()
        tempo = str(self.tempo(self.mes_contrato, self.ano_contrato))
        invoice_vals['reference'] = '%s(%s)-%s-%s' %(
            self.name, tempo, str(today.month).zfill(2), today.year)
        invoice_vals['type'] = 'out_invoice'
        return invoice_vals

    @api.model
    def create(self, vals):
        ctr = super(AccountAnalyticAccount, self).create(vals)
        if 'imovel_id' in vals:
            imovel = self.env['imovel'].browse(vals['imovel_id'])
            imovel.write({'alugado': True})
        return ctr
        
    """
    @api.onchange('active')
    def onchange_active(self):
        import pudb;pu.db
        if not self.active:
            imovel = self.env['imovel'].browse([self.imovel_id.id])
            imovel.write({'alugado': False})
            self.name = ''
    """
                    
    @api.multi
    def write(self, values):
        if 'imovel_id' in values and self.active:
            raise UserError(
                _("Contrato já ativado, para trocar o imovel, inative o contrato")
                )
        if 'active' in values and not values['active']:
            # altero o imovel anterior
            imovel = self.env['imovel'].browse([self.imovel_id.id])
            imovel.write({'alugado': False})
        if 'imovel_id' in values:
            # altero o imovel atual
            imovel = self.env['imovel'].browse(values['imovel_id'])
            imovel.write({'alugado': True})
        return super(AccountAnalyticAccount, self).write(values)


class AccountAnalyticContractLine(models.Model):
    _inherit = 'account.analytic.contract.line'

    repassa_prop = fields.Boolean(
        string="Repassa Propriet.?",
        help="Repassa este valor para o Proprietario ",
    )
