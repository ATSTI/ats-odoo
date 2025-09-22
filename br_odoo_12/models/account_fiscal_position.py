# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountFiscalPositionTemplate(models.Model):
    _inherit = 'account.fiscal.position.template'

    ind_final = fields.Selection([
        ('0', 'Não'),
        ('1', 'Consumidor final')
    ], 'Operação com Consumidor final',
        help='Indica operação com Consumidor final.')
    ind_pres = fields.Selection([
        ('0', 'Não se aplica'),
        ('1', 'Operação presencial'),
        ('2', 'Operação não presencial, pela Internet'),
        ('3', 'Operação não presencial, Teleatendimento'),
        ('4', 'NFC-e em operação com entrega em domicílio'),
        ('5', 'Operação presencial, fora do estabelecimento'),
        ('9', 'Operação não presencial, outros'),
    ], 'Tipo de operação',
        help='Indicador de presença do comprador no\n'
             'estabelecimento comercial no momento\n'
             'da operação.', default='0')


class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    finalidade_emissao = fields.Selection(
        [('1', 'Normal'),
         ('2', 'Complementar'),
         ('3', 'Ajuste'),
         ('4', 'Devolução')],
        'Finalidade', help=u"Finalidade da emissão de NFe", default="1")
    ind_final = fields.Selection([
        ('0', 'Não'),
        ('1', 'Sim')
    ], 'Consumidor final?',
        help='Indica operação com Consumidor final. Se não utilizado usa\
        a seguinte regra:\n 0 - Normal quando pessoa jurídica\n1 - Consumidor \
        Final quando for pessoa física')
    ind_pres = fields.Selection([
        ('0', 'Não se aplica'),
        ('1', 'Operação presencial'),
        ('2', 'Operação não presencial, pela Internet'),
        ('3', 'Operação não presencial, Teleatendimento'),
        ('4', 'NFC-e em operação com entrega em domicílio'),
        ('5', 'Operação presencial, fora do estabelecimento'),
        ('9', 'Operação não presencial, outros'),
    ], 'Tipo de operação',
        help='Indicador de presença do comprador no\n'
             'estabelecimento comercial no momento\n'
             'da operação.', default='0')
    # TODO Fazer este campo gerar mensagens dinamicas
    note = fields.Text('Observações')


# class AccountFiscalPositionTax(models.Model):
#     _inherit = 'account.fiscal.position.tax'

#     state_ids = fields.Many2many('res.country.state', string="Estados")
