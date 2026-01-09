from odoo import models, fields

class EventEvent(models.Model):
    _inherit = 'event.event'

    tipo_evento = fields.Selection(
        [
            ('owd', 'OWD'),
            ('profundo', 'PROFUNDO'),
            ('turismo', 'TURISMO'),
            ('especialidades', 'ESPECIALIDADES'),
            ('outro', 'Outro'),
        ],
        string="Tipo de Evento",
        required=True
    )

    def action_call_equipamentos(self):
        for event in self:
            registrations = self.env['event.registration'].search([
                ('event_id', '=', event.id)
            ])
            registrations._assign_equipamentos()
        return True
    
    def action_limpar_equipamentos(self):
        PartnerEquip = self.env['partner.equipamento']

        for event in self:
            for reg in event.registration_ids:
                partner = reg.partner_id
                if reg.bcd_id:
                    equipamento_proprio = PartnerEquip.search([
                        ('partner_id', '=', partner.id),
                        ('product_id', '=', reg.bcd_id.id),
                        ('is_loan', '=', False),
                    ], limit=1)

                    if not equipamento_proprio:
                        reg.bcd_id.usado = False
                    reg.bcd_id = False
                if reg.suit_id:
                    equipamento_proprio = PartnerEquip.search([
                        ('partner_id', '=', partner.id),
                        ('product_id', '=', reg.suit_id.id),
                        ('is_loan', '=', False),
                    ], limit=1)

                    if not equipamento_proprio:
                        reg.suit_id.usado = False

                    reg.suit_id = False
        return True


