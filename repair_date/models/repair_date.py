# © 2018  Carlos R. Silveira
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from ast import literal_eval
from odoo import api, fields, models, _
from datetime import datetime

class RepairOrder(models.Model):
    _inherit = 'repair.order'
    
    data_validacao = fields.Date(string='Data de validação')

    date_repair = fields.Date(string='Data ordem serviço',
        index=True, readonly=True, default=fields.Date.context_today)
    date_repair_closed = fields.Date(string='Data fechamento',
        index=True, readonly=True,)