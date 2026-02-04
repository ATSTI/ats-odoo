# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp


class ItensTransacao(models.Model):
    _name = 'itens.transacao'
    _description = 'Transação de Materiais Internos'

    name = fields.Char(string='Número', required=True, copy=False, readonly=True, default='/')
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env['res.company']._company_default_get('account.account'))
    
    material_request_line_ids = fields.One2many(
        'itens.requisitados',
        'transacao_id',
        string='Materiais'
    )
    obs_req = fields.Char(string='Observação')
    who_req = fields.Char(string='Requirente')
    date_req = fields.Date(string='Data de Requisição')

    material_devolution_line_ids = fields.One2many(
        'itens.devolvidos',
        'transacao_id',
        string='Materiais'
    )
    obs_devol = fields.Char(string='Observação')
    who_devol = fields.Char(string='Restintuinte')
    date_devol = fields.Date(string='Data de Devolução')

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('itens.transacao') or '/'
        return super(ItensTransacao, self).create(vals)

class ItensRequisitados(models.Model):
    _name = 'itens.requisitados'
    _description = 'Linha de Requisição (livre)'

    transacao_id = fields.Many2one(
        'itens.transacao',
        ondelete='cascade'
    )

    item = fields.Char(string='Item', required=True)
    quantidade = fields.Float(string='Quantidade', default=1)
    

class ItensDevolvidos(models.Model):
    _name = 'itens.devolvidos'
    _description = 'Linha de Devolução (livre)'

    transacao_id = fields.Many2one(
        'itens.transacao',
        ondelete='cascade'
    )

    item = fields.Char(string='Item', required=True)
    quantidade = fields.Float(string='Quantidade', default=1)
    
