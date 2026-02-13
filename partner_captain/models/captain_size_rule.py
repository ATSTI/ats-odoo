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

    def _normalizar_altura_vals(self, vals):
        if 'altura' in vals and vals['altura']:
            if vals['altura'] < 3:
                vals['altura'] = vals['altura'] * 100
        return vals

    @api.onchange('altura')
    def _onchange_altura(self):
        if self.altura and self.altura < 3:
            self.altura = self.altura * 100


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
                    "(Gênero, Seleção, Altura, Peso)."
                )


    def _recalcular_tamanhos_parceiros(self):
        if self.env.context.get('captain_recalc_done'):
            return

        generos = self.mapped('genero')

        partners = self.env['res.partner'].with_context(
            captain_recalc_done=True
        ).search([
            ('genero', 'in', generos),
            ('peso', '!=', False),
            ('altura', '!=', False),
        ])

        partners._compute_tamanhos()

    @api.model
    def create(self, vals):
        vals = self._normalizar_altura_vals(vals)
        rec = super().create(vals)
        rec._recalcular_tamanhos_parceiros()
        return rec

    def write(self, vals):
        vals = self._normalizar_altura_vals(vals)
        res = super().write(vals)

        if self._CAMPOS_RELEVANTES.intersection(vals.keys()):
            self._recalcular_tamanhos_parceiros()

        return res

    def unlink(self):
        res = super().unlink()
        self._recalcular_tamanhos_parceiros()
        return res
