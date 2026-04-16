from odoo import models, fields

class EventLocation(models.Model):
    _name = 'event.location'
    _description = 'Local do Evento'

    name = fields.Char(
        string='Local',
        required=True
    )

    street = fields.Char(string='Rua')
    street2 = fields.Char(string='Complemento')
    city = fields.Char(string='Cidade')
    state_id = fields.Many2one(
        'res.country.state',
        string='Estado'
    )
    zip = fields.Char(string='CEP')
    country_id = fields.Many2one(
        'res.country',
        string='País'
    )

    notes = fields.Text(string='Observações')
