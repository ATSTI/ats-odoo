# -*- coding: utf-8 -*-
# © 2018  Carlos R. Silveira
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    contatonome = fields.Char(string='Contato Emergência')
    contatofone = fields.Char(string='Telefone Emergência')
    birthdate_date = fields.Date('Data de Nascimento')
    firstname = fields.Char(string='Prim. Nome')
    rg_emissao = fields.Date(string='Data Emissao')
    rg_orgao = fields.Char(string='Orgão emissor', size=30)
    cnh = fields.Char(string='CNH', size=30)
    cnh_emissao = fields.Date(string='Data Emissao')
    cnh_primhabilita = fields.Date(string='Data Prim. Habilitação')
    cnh_vcto = fields.Date(string='Data Vencimento')
    revised = fields.Boolean(string='Revisado')
    estado_civil = fields.Selection([
        ('cel','Solteiro'),
        ('maried','Casado'),
        ('pacs', 'União Civil'),
        ('divorced','Divorciado'), 
        ('viuvo', 'Viúvo')], 'Estado Civil')
    sexo = fields.Selection([
        ('F', 'Feminino'),
        ('M', 'Masculino')], 'Sexo')
       

    # vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


    def gerar_pipeline(self):
        active_ids = self.env.context.get('active_ids')                                                                                                                    
        if self.env.context.get('active_model') == 'res.partner' and active_ids:                                                                                           
            res['state'] = 'selection'                                                                                                                                     
            res['partner_ids'] = active_ids                                                                                                                                
            res['dst_partner_id'] = self._get_ordered_partner(active_ids)[-1].id 




