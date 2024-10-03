# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, _, api
from datetime import datetime, date
from odoo.exceptions import ValidationError
import base64
import tempfile
import time
import xlrd
import re
import os.path
from erpbrasil.base.fiscal import cnpj_cpf, ie


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_copiar_fatura(self):
        self.copy()

