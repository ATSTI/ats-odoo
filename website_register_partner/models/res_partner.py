from odoo import models, fields, api

class Partner(models.Model):
    _inherit = 'res.partner'

    cursos = fields.Many2many(
        'sindicato.cursos',
        string='Cursos',
        store=True
    )
    
    nascimento = fields.Date(string="Data de Nascimento")

    identificacao = fields.Selection(
        [('associado', 'Associado'),
          ('outro', 'Outro'),
          ('produtor_rural', 'Produtor Rural'),
          ('trabalhador_rural', 'Trabalhador Rural')],
        string='Identificação',
    )
    grau_escolar = fields.Selection(
        [('dr', 'Doutorado'),
          ('sup', 'Ensino Superior'),
          ('medio_compl', 'Ensino Médio Completo'),
          ('medio_incom', 'Ensino Médio Incompleto'),
          ('fund_compl', 'Ensino Fundamental Completo'),
          ('fund_incom', 'Ensino Fundamental Incompleto')],
        string='Grau de Escolaridade',
    )
    curso_senar = fields.Boolean(
        string="Participou do Curso do SENAR",
    )
    redes_sociais = fields.Many2many(
        'res.partner.redes_sociais',
        string='Redes Sociais',
    )

class RedesSociais(models.Model):
    _name = 'res.partner.redes_sociais'
    _description = "Redes Sociais"

    name = fields.Char("Nome da Rede Social", required=True)



class Cursos(models.Model):
    _name = 'sindicato.cursos'
    _description = "Cursos do Sindicato"

    name = fields.Char("Nome do Curso", required=True)
        



    



   