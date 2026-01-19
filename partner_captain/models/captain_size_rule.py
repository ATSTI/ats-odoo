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
