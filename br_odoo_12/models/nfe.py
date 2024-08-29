# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models

class NfeReboque(models.Model):
    _name = 'nfe.reboque'
    _description = "NF-e Reboque"

    invoice_eletronic_id = fields.Many2one('br_odoo.nfe', string="NFe")
    placa_veiculo = fields.Char(string="Placa", size=7)
    uf_veiculo = fields.Char(string=u"UF Veículo", size=2)
    rntc = fields.Char(string="RNTC", size=20,
                       help="Registro Nacional de Transportador de Carga")
    vagao = fields.Char(string=u"Vagão", size=20)
    balsa = fields.Char(string="Balsa", size=20)


class NfeVolume(models.Model):
    _name = 'nfe.volume'
    _description = "NF-e Volume"

    invoice_eletronic_id = fields.Many2one('br_odoo.nfe', string="NFe")
    quantidade_volumes = fields.Integer(string="Qtde. Volumes")
    especie = fields.Char(string=u"Espécie", size=60)
    marca = fields.Char(string="Marca", size=60)
    numeracao = fields.Char(string=u"Numeração", size=60)
    peso_liquido = fields.Float(string=u"Peso Líquido")
    peso_bruto = fields.Float(string="Peso Bruto")


class NFeCobrancaDuplicata(models.Model):
    _name = 'nfe.duplicata'
    _description = "NF-e Duplicata"
    _order = 'data_vencimento'

    invoice_eletronic_id = fields.Many2one('br_odoo.nfe', string="NFe")
    currency_id = fields.Many2one(
        'res.currency', related='invoice_eletronic_id.currency_id',
        string="EDoc Currency", readonly=True)
    numero_duplicata = fields.Char(string=u"Número Duplicata", size=60)
    data_vencimento = fields.Date(string="Data Vencimento")
    valor = fields.Monetary(string="Valor Duplicata")