from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CaptainSizeRule(models.Model):
    _name = 'captain.size.rule'
    _description = 'Tabela de Tamanhos'

    name = fields.Char(string="Descrição")

    genero = fields.Selection(
        [('masculino', 'Masculino'), ('feminino', 'Feminino')],
        required=True
    )

    selecao = fields.Selection(
        [('suit', 'Suit'), ('bcd', 'BCD')],
        required=True
    )

    altura = fields.Float(string="Altura (cm)", required=True)
    peso = fields.Float(string="Peso (kg)", required=True)

    tamanho = fields.Selection(
        [
            ("jr", "JR"),
            ("pp", "PP"),
            ("p", "P"),
            ("pl", "PL"),
            ("m", "M"),
            ("ml", "ML"),
            ("g", "G"),
            ("xl", "XL"),
        ],
        string="Tamanho CD",
        required=True
    )


    _CAMPOS_RELEVANTES = {
        'genero',
        'selecao',
        'altura',
        'peso',
        'tamanho',
    }

    @api.constrains('genero', 'selecao', 'altura', 'peso', 'tamanho')
    def _check_tamanho_duplicado(self):
        for rec in self:
            domain = [
                ('id', '!=', rec.id),
                ('genero', '=', rec.genero),
                ('selecao', '=', rec.selecao),
                ('altura', '=', rec.altura),
                ('peso', '=', rec.peso),
            ]

            if self.search_count(domain) > 0:
                raise ValidationError(
                    "Tamanho já cadastrado para essa configuração "
                    "(Gênero, Seleção, Altura, Peso e Tamanho)."
                )
    def _recalcular_tamanhos_parceiros(self):
        """
        Recalcula os tamanhos de todos os parceiros.
        Executa apenas uma vez por transação.
        """
        if self.env.context.get('captain_recalc_done'):
            return
        partners = self.env['res.partner'].search([])
        partners._compute_tamanhos()
        self = self.with_context(captain_recalc_done=True)
    @api.model
    def create(self, vals):
        record = super().create(vals)
        record._recalcular_tamanhos_parceiros()
        return record

    def write(self, vals):
        res = super().write(vals)
        if self._CAMPOS_RELEVANTES.intersection(vals.keys()):
            self._recalcular_tamanhos_parceiros()
        return res

    def unlink(self):
        res = super().unlink()
        self._recalcular_tamanhos_parceiros()
