from . import models
from odoo import _
import logging
_logger = logging.getLogger(__name__)

def post_load_constants(cr, registry):
    # força o carregamento das constantes antes do CSV
    _logger.info(_("Loading l10n_br_fiscal post init files. It may take a minute..."))
    from .models import fiscal_constants_adic