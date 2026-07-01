# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    l10n_br_use_boleto_bradesco = fields.Boolean('Emitir Boleto Bradesco')
    l10n_br_bradesco_cert = fields.Binary('Certificado API Bradesco')
    l10n_br_bradesco_key = fields.Binary('Chave API Bradesco')
    l10n_br_bradesco_token = fields.Char('Token oAuth Bradesco')
    l10n_br_bradesco_id = fields.Char('Id Bradesco')
    l10n_br_bradesco_secret = fields.Char('Senha Bradesco')

    l10n_br_valor_multa = fields.Float(string="Valor da Multa (%): ")
    l10n_br_valor_juros_mora = fields.Float(string="Valor Juros Mora (%): ")
    l10n_br_boleto_instrucoes = fields.Char(string="Instruções do Boleto", size=400)
    tipo_ambiente_boleto = fields.Selection(
        [("1", u"Produção"), ("2", u"Homologação")],
        string="Ambiente Emissão boleto",
        default="2",
    )
