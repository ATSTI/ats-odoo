from odoo import models, _
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def action_send_msg(self):
        """Abre o wizard personalizado de WhatsApp com templates e preview."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Send WhatsApp Message'),
            'res_model': 'chatwoot.composer',  
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_partner_id': [(6, 0, [self.id])], 
                'default_model': 'res.partner',
                'default_res_id': self.id,
            },
        }
