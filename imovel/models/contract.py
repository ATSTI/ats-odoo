# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import date


class ContractContract(models.Model):
    _inherit = "contract.contract"

    imovel_id = fields.Many2one(
        'imovel',
        string='Imovel',
        required=True
        )

    proprietario_ids = fields.Many2many(
        comodel_name='owner.line',
        string='Proprietario',
    )

    @api.onchange('imovel_id')
    def onchange_imovel_id(self):
        if self.imovel_id:
            # for prop in self.imovel_id.owner_ids:
            self.proprietario_ids = self.imovel_id.owner_ids
            #     self.create({'proprietario_ids': [(0, prop.id)]})
            self.name = self.imovel_id.name
            today = date.today()
            self.code = '%s-%s-%s' %(
                self.imovel_id.name, 
                str(today.month).zfill(2),
                str(today.year)
                )
        return {}
        
    @api.model
    def _prepare_invoice(self, date_invoice, journal=None):
        invoice_vals = super(ContractContract, self).\
            _prepare_invoice(date_invoice, journal)
        # if self.payment_mode_id:
        #     invoice_vals['payment_mode_id'] = self.payment_mode_id.id
        #     #invoice_vals['partner_bank_id'] = (
        #     #    contract.partner_id.bank_ids[:1].id or
        #     #    contract.payment_mode_id.bank_id.id)
        # if self.payment_term_id:
        #     invoice_vals['payment_term_id'] = self.payment_term_id.id
        # if self.fiscal_position_id:
        #     invoice_vals['fiscal_position_id'] = self.fiscal_position_id.id
        today = date.today()
        # tempo = str(self.mes_contrato, self.ano_contrato))
        invoice_vals[0].update({
            'contract_id': self.id,
            'ref': '%s-%s-%s' %(
                self.name, str(today.month).zfill(2), today.year),
            
        })
        # 'type': 'out_invoice',
        return invoice_vals

    @api.model
    def create(self, vals):
        ctr = super(ContractContract, self).create(vals)
        if 'imovel_id' in vals:
            imovel = self.env['imovel'].browse(vals['imovel_id'])
            imovel.write({'alugado': True})
        return ctr
        
    @api.onchange('active')
    def onchange_active(self):
        if not self.active:
            imovel = self.env['imovel'].browse([self.imovel_id.id])
            imovel.write({'alugado': False})
            self.name = ''
                    
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
        return super(ContractContract, self).write(values)


class ContractLine(models.Model):
    _inherit = "contract.line"

    repassa_prop = fields.Boolean(
        string="Repassa Propriet.?",
        help="Repassa este valor para o Proprietario ",
    )
