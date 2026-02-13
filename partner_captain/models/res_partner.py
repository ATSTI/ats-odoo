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
    nadadeira = fields.Text(string='Nadadeira')
    genero = fields.Selection([
        ("masculino",'Masculino'),
        ('feminino','Feminino'),
    ], string ='Gênero')
    contatonome = fields.Char(string='Contato Emergência')
    contatofone = fields.Char(string='Telefone Emergência')
    alergia= fields.Char(string='Alergia')
    medicacao = fields.Char(string='Medicação')
    restricaoalimentar = fields.Char(string='Restrição Alimentar')
    segurodan = fields.Char(string='Seguro DAN')
    passaporte = fields.Char(string='Passaporte')
    birthdate_date = fields.Date("Data de Nascimento")
    equipamento_ids = fields.One2many(
        'partner.equipamento',
        'partner_id',
        string='Equipamentos'
    )
    tem_equipamento = fields.Boolean(
        string='Possui Equipamento próprio?'
    )
    bcd = fields.Text(
        "BCD",
        compute="_compute_tamanhos",
        store=True
    )

    suit = fields.Text(
        "SUIT",
        compute="_compute_tamanhos",
        store=True
    )
    bag = fields.Text(string="BAG", store=True)
    reg = fields.Text(string="REG", store=True)

    equipamento_movimento_ids = fields.One2many(
        'partner.equipamento.movimento',
        'partner_id',
        string='Movimentações de Equipamentos'
    )

    def write(self, vals):
        if 'equipamento_ids' in vals:
            for command in vals['equipamento_ids']:
                # (2, id) = remover linha
                # (3, id) = remover vínculo
                if command[0] in (2, 3):
                    self.env['partner.equipamento'].browse(command[1]).unlink()

        return super().write(vals)


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

    @api.depends('peso', 'altura', 'genero')
    def _compute_tamanhos(self):
        SizeRule = self.env['captain.size.rule']

        for partner in self:
            partner.bcd = False
            partner.suit = False

            if not partner.peso or not partner.altura:
                continue

            if partner.genero not in ('masculino', 'feminino'):
                continue

            # se altura estiver em metros → converter pra cm
            altura = partner.altura * 100 if partner.altura < 3 else partner.altura

            peso = partner.peso

            # margens
            peso_ref = peso + 3
            altura_ref = altura + 2

            def buscar_tamanho(selecao):
                rule = SizeRule.search([
                    ('genero', '=', partner.genero),
                    ('selecao', '=', selecao),
                    ('altura', '>=', altura),
                    ('peso', '>=', peso),
                ], order='altura asc, peso asc', limit=1)

                if rule:
                    return rule

                return SizeRule.search([
                    ('genero', '=', partner.genero),
                    ('selecao', '=', selecao),
                    ('altura', '>=', altura_ref),
                    ('peso', '>=', peso_ref),
                ], order='altura asc, peso asc', limit=1)

            bcd_rule = buscar_tamanho('bcd')
            suit_rule = buscar_tamanho('suit')

            partner.bcd = bcd_rule.tamanho if bcd_rule else False
            partner.suit = suit_rule.tamanho if suit_rule else False



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
