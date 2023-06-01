# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError


class CrmPipelineCreate(models.TransientModel):
    """
    Este Wizard cria pipeline para todos parceiros selecionados
    """

    _name = "crm.pipeline.create"
    _description = "Criar Pipeline Parceiros"
    
    titulo = fields.Char(string='Título Pipeline')

    def pipeline_create(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        
        prd = []
        if context['active_model'] == 'partner.historico':
            for prt in self.env['partner.historico'].browse(active_ids):
                if prt.partner_id.id in prd:
                    continue
                prd.append(prt.partner_id.id)
        else:
            for prt in self.env['res.partner'].browse(active_ids):
                prd.append(prt.partner_id.id)
        
        for partner in self.env['res.partner'].browse(prd):
            vals = {
                'name': self.titulo,
                'partner_name': partner.name,
                'contact_name': partner.name if not partner.is_company else False,
                'title': partner.title.id,
                'street': partner.street,
                'street2': partner.street2,
                'city': partner.city,
                'state_id': partner.state_id.id,
                'country_id': partner.country_id.id,
                'email_from': partner.email,
                'phone': partner.phone,
                'mobile': partner.mobile,
                'zip': partner.zip,
                'function': partner.function,
                'website': partner.website,
                'partner_id': partner.id,
            }
            self.env['crm.lead'].create(vals)
        return {'type': 'ir.actions.act_window_close'}
