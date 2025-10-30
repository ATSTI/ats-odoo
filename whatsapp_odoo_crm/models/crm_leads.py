from odoo import models, _
from odoo.exceptions import UserError

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    def action_send_msg(self):
        """Abre o wizard personalizado de WhatsApp com templates e preview."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Enviar mensagem no whatsapp'),
            'res_model': 'whatsapp.evolution.composer',  
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_partner_id': [(6, 0, [self.partner_id.id])], 
                'default_model': 'crm.lead',
                'default_res_id': self.id,
            },
        }
