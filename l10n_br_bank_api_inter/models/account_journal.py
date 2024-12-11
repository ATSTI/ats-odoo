# Copyright 2023 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from datetime import datetime


class AccountJournal(models.Model):

    _inherit = "account.journal"

    bank_inter_cert = fields.Binary(string="Bank Inter Certificate")

    bank_inter_key = fields.Binary(string="Bank Inter Key")

    bank_client_id = fields.Char(
        string="Client ID",
        help="Client ID provided by the bank",
    )

    bank_secret_id = fields.Char(
        string="Secret ID",
        help="Secret ID provided by the bank",
    )

    bank_environment = fields.Selection(
        selection=[("1", "Produção"), ("2", "Homologação")],
        string="Ambiente",
        default="2",
    )

    bank_token = fields.Char(string="Token escrita", readonly=True)
    bank_token_date = fields.Datetime(string="Data token escrita", readonly=True, default=datetime.now())

    bank_token_read = fields.Char(string="Token consulta", readonly=True)
    bank_token_date_read = fields.Datetime(string="Data toke consulta", readonly=True, default=datetime.now())
    bank_multa_type = fields.Selection(
        selection=[("VALORFIXO", "Valor fixo"), ("PERCENTUAL", "Percentual")],
        string="Tipo Multa",
        default="PERCENTUAL",
    )
    bank_multa_value = fields.Float('Valor multa', digits=(16, 2))
    bank_mora_type = fields.Selection(
        selection=[("VALORDIA", "Valor dia"), ("TAXAMENSAL", "Taxa mensal")],
        string="Tipo Juros",
        default="VALORDIA",
    )
    bank_mora_value = fields.Float('Valor juros', digits=(16, 2))    