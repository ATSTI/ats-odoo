# -*- coding: utf-8 -*-
# © 2018  Carlos R. Silveira
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    #equipamento_ids = fields.Many2many('crm.historico', string='Equipamento/Curso/Viagem')
    historico_line = fields.One2many('partner.historico', 'partner_id', string='Equipamento/Curso/Viagem')
    peso = fields.Integer(string='Peso')
    altura = fields.Float(string='Altura')
    calcado = fields.Integer(string='Calçado')
    contatonome = fields.Char(string='Contato Emergência')
    contatofone = fields.Char(string='Telefone Emergência')
    alergia= fields.Char(string='Alergia')
    medicacao = fields.Char(string='Medicação')
    restricaoalimentar = fields.Char(string='Restrição Alimentar')
    segurodan = fields.Char(string='Seguro DAN')
    passaporte = fields.Char(string='Passaporte')
    birthdate_date = fields.Date("Data de Nascimento")
    	            
       

    # vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


    def gerar_pipeline(self):
        active_ids = self.env.context.get('active_ids')                                                                                                                    
        if self.env.context.get('active_model') == 'res.partner' and active_ids:                                                                                           
            res['state'] = 'selection'                                                                                                                                     
            res['partner_ids'] = active_ids                                                                                                                                
            res['dst_partner_id'] = self._get_ordered_partner(active_ids)[-1].id 

    @api.onchange('name')
    def _onchange_name(self):
        if self.name and self.company_type == "person":
            self.legal_name = self.name

class PartnerHistorico(models.Model):
    _name = "partner.historico"
    _order = 'data_aquisicao'
    _rec_name = 'data_aquisicao'

    partner_id = fields.Many2one('res.partner', string='Parceiro')
    venda_id = fields.Many2one('sale.order', string='Venda')
    historico_id = fields.Many2many('crm.historico', required=True)
    data_aquisicao = fields.Date(string='Data Aquisiçao', default=datetime.now())

    """
    @api.model
    def create(self, vals):
        hist = self.env['crm.historico'].browse(vals['historico_id'])
        vals['tipo'] = hist.tipo
        return super(PartnerHistorico, self).create(vals)
    """
    """  nao permite excluir o pedido se deixar isso.
    @api.multi
    def unlink(self):
        if self.venda_id:
            raise UserError(_('Item inserido por vendas, \npara excluir somente cancelando o pedido.'))
        return super(Equipamentos, self).unlink()
    """
