from odoo import fields, models, api
from datetime import datetime

class PartnerEquipamento(models.Model):
    _name = 'partner.equipamento'
    _description = 'Equipamentos do Cliente'

    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        required=True,
        ondelete='cascade'
    )
    movimento_ids = fields.One2many(
    'partner.equipamento.movimento',
    'equipamento_id',
    string='Movimentações'
)
    tipo = fields.Selection([
        ('bcd', 'BCD'),
        ('suit', 'SUIT'),
        ('reg', 'REG'),
        ('bag', 'BAG'),
    ], string='Tipo de equipamento', required=True)

    obs = fields.Char(string='Observação')
    dias_na_captain = fields.Integer(
        compute='_compute_status_captain',
        store=True
    )
    em_atraso = fields.Boolean(
        compute='_compute_status_captain',
        store=True
    )
    ultimo_movimento = fields.Selection(
        [('entrada', 'Entrada'), ('saida', 'Saída')],
        compute='_compute_status_captain',
        store=True
    )
    def name_get(self):
        result = []
        tipo_dict = dict(self._fields['tipo'].selection)

        for rec in self:
            tipo_label = tipo_dict.get(rec.tipo, '').upper()
            motivo = rec.obs or 'SEM OBSERVAÇÃO'
            nome = f'{motivo} - {tipo_label}'
            result.append((rec.id, nome))

        return result

    @api.depends('movimento_ids.data_movimento', 'movimento_ids.movimento')
    def _compute_status_captain(self):
        for eq in self:
            eq.dias_na_captain = 0
            eq.em_atraso = False
            eq.ultimo_movimento = False
            if not eq.movimento_ids:
                continue
            ultimo = eq.movimento_ids.sorted(
                key=lambda m: m.data_movimento or fields.Datetime.now(),
                reverse=True
            )[0]
            eq.ultimo_movimento = ultimo.movimento
            if ultimo.movimento == 'entrada':
                delta = fields.Datetime.now() - ultimo.data_movimento
                dias = delta.days
                eq.dias_na_captain = dias
                eq.em_atraso = dias >= 1

    def write(self, vals):
        if 'movimento_ids' in vals:
            for command in vals['movimento_ids']:
                if command[0] == 2:
                    self.env['partner.equipamento.movimento'].browse(command[1]).unlink()
        return super().write(vals)
