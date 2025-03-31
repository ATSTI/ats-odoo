# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models
from collections import defaultdict


class AccountMove(models.Model):

    _inherit = "account.move"

    fatura_duplicata = fields.Boolean('Duplicata da Fatura?', default=True)
