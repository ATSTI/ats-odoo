# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models


class DocumentNfe(models.Model):
    _inherit = "l10n_br_fiscal.document"

    nfe40_vICMSDeson = fields.Monetary(related="amount_icms_relief_value")