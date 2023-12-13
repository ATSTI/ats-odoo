# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, _
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
        ]
        contract = self.search(base_domain)
        for ctr in contract:
            crm_lead = self.env["crm.lead"].search([
                ('name', '=', ctr.name),
                ('partner_id', '=', ctr.partner_id.id),
                ('stage_id', '=', 1)
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
        
