# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

def post_init_hook(cr, registry):
    """Copiar campos br_base Trust."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    partner = env["res.partner"].search([])

    for prt in partner:
        prt.city_id_bkp = prt.city_id.id
        prt.cnpj_cpf_bkp = prt.cnpj_cpf