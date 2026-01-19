# -*- coding: utf-8 -*-

from odoo import fields, models, _, api

class CrmHistorico(models.Model):
    _name = 'crm.historico'
    _description = "Cadastro de Equipamentos, Cursos e Viagens"
    _order = 'sequence'

    name = fields.Char(string="Descrição")
    sequence = fields.Integer(u'Sequência', default=1, required=True)
    tipo = fields.Selection([
        ('c', 'Curso'),
        ('e', 'Equipamento'),
        ('v', 'Viagem'),
        ], string='Tipo')

