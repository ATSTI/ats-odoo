# -*- coding: utf-8 -*-
from odoo import fields, models

class AccountMove(models.Model):
    _inherit = "account.move"

    # Campo relacionado ao website do parceiro, armazenado no banco e somente leitura.
    partner_website = fields.Char(
        string="Website do Cliente",
        related="partner_id.website",
        store=True,
        readonly=True,
        help="Espelha o campo Website do parceiro e persiste no registro da fatura."
    )