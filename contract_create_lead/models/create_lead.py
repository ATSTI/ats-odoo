# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from datetime import datetime


class ContractContractLead(models.Model):
    _inherit = 'contract.contract'

    def action_create_crm_lead(self):
        hj = datetime.now()
        ultimo_dia = (hj + relativedelta(day=31))
        if hj.month+2 > 12:
            mes = hj.month+2-12
            mes_seguinte = hj.replace(month=mes, year=hj.year+1)
        else:
            mes_seguinte =  hj.replace(month=hj.month+2)
        primeiro_dia = mes_seguinte.replace(day=1)
        base_domain = [
            ('date_end', '>', ultimo_dia), 
            ('date_end','<', primeiro_dia),
            ('tipo', 'not in', ['saude']),
        ]
        contract = self.search(base_domain)
        if hj.month+3 > 12:
            mes = hj.month+3-12
            mes_seguinte = hj.replace(month=mes, year=hj.year+1)
        else:
            mes_seguinte =  hj.replace(month=hj.month+3)
        primeiro_dia = mes_seguinte.replace(day=1)
        ultimo_dia = (mes_seguinte + relativedelta(day=31))
        base_domain_saude = [
            ('date_end', '<', ultimo_dia), 
            ('date_end','>', primeiro_dia),
            ('tipo', '=', ['saude']),
        ]
        contract += self.search(base_domain_saude)    
        for ctr in contract:
            crm_lead = self.env["crm.lead"].search([
                ('name', '=', ctr.name),
                ('partner_id', '=', ctr.partner_id.id),
                ('stage_id', '=', 1)
                ('contract_id', '=', ctr.id)
            ])
            if crm_lead:
                continue 
            vals={
                "name": ctr.name,
                "partner_id": ctr.partner_id.id,
            }
            lead = self.env["crm.lead"].create(vals)
            self.message_post(
                body=_("Criado a Lead <b>%s<b> " %(lead.name)),
                subject=_("Criado uma oportunidade"),
                message_type="notification"
            )

class Lead(models.Model):
    _inherit = 'crm.lead'
        
    contract_id = fields.Float('Id do Contrato')

    @api.model
    def action_set_lost(self):
        # """ Lost semantic: probability = 0, active = False """
        # return self.write({'probability': 0, 'active': False})
        contract_lost = super(Lead, self).\
            action_set_lost()
        
        return contract_lost

    @api.model
    def action_set_won(self):
        """ Won semantic: probability = 100 (active untouched) """
        for lead in self:
            stage_id = lead._stage_find(domain=[('probability', '=', 100.0), ('on_change', '=', True)])
            lead.write({'stage_id': stage_id.id, 'probability': 100})
        contract_won = super(Lead, self).\
            action_set_won()
        
        return contract_won