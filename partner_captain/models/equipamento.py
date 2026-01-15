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

    tipo = fields.Selection([
        ('bcd', 'BCD'),
        ('suit', 'SUIT'),
        ('reg', 'REG'),
        ('bag', 'BAG'),
    ], string='Tipo de equipamento', required=True)

    obs = fields.Char(string='Observação')

    # 🔥 NOVOS CAMPOS
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

    @api.depends('partner_id')
    def _compute_status_captain(self):
        Movimento = self.env['partner.equipamento.movimento']

        for eq in self:
            ultimo = Movimento.search(
                [('equipamento_id', '=', eq.id)],
                order='data_movimento desc',
                limit=1
            )

            eq.dias_na_captain = 0
            eq.em_atraso = False
            eq.ultimo_movimento = False

            if ultimo:
                eq.ultimo_movimento = ultimo.movimento

                if ultimo.movimento == 'entrada':
                    delta = datetime.now() - ultimo.data_movimento
                    dias = delta.days
                    eq.dias_na_captain = dias
                    eq.em_atraso = dias >= 7
