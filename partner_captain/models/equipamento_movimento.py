from odoo import fields, models
class PartnerEquipamentoMovimento(models.Model):
    _name = 'partner.equipamento.movimento'
    _description = 'Movimentação de Equipamento'
    _order = 'data_movimento desc'

    equipamento_id = fields.Many2one(
        'partner.equipamento',
        string='Equipamento',
        required=True,
        ondelete='cascade'
    )

    partner_id = fields.Many2one(
        related='equipamento_id.partner_id',
        store=True,
        string='Cliente'
    )

    tipo = fields.Selection(
        related='equipamento_id.tipo',
        store=True,
        string='Tipo'
    )

    movimento = fields.Selection([
        ('entrada', 'Entrada na Captain'),
        ('saida', 'Saída para o Cliente'),
    ], required=True)

    data_movimento = fields.Datetime(
        string='Data do Movimento',
        default=fields.Datetime.now,
        required=True
    )

    motivo = fields.Char(string='Motivo')

    user_id = fields.Many2one(
        'res.users',
        string='Responsável',
        default=lambda self: self.env.user
    )
