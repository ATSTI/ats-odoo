from odoo import models, fields

class CaptainSizeRule(models.Model):
    _name = 'captain.size.rule'
    _description = 'Tabela de Tamanhos'

    name = fields.Char(string="Descrição", required=False)

    genero = fields.Selection([
        ('masculino', 'Masculino'),
        ('feminino', 'Feminino'),
    ], required=True)

    selecao = fields.Selection([
        ('suit', 'Suit'),
        ('bcd', 'Bcd'),
    ], required=True)

    altura = fields.Float(string="Altura (cm)", required=True)
    peso = fields.Float(string="Peso (kg)", required=True)
    tamanho = fields.Char(string="Tamanho", required=True)
