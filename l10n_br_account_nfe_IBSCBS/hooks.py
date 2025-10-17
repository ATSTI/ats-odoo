import logging
from odoo import SUPERUSER_ID, _, api, tools

_logger = logging.getLogger(__name__)

def post_init_hook(cr, registry):
    """Import XML/CSV data to initialize fiscal groups and taxes"""
    env = api.Environment(cr, SUPERUSER_ID, {})

    group_files = [
        "data/l10n_br_fiscal.tax.group.csv",
    ]
    _logger.info(_("Loading tax group files..."))
    for file in group_files:
        tools.convert_file(
            cr,
            "l10n_br_account_nfe_IBSCBS",
            file,
            None,
            mode="init",
            noupdate=True,
            kind="init",
        )

    groups = env['account.tax.group'].search([('name', 'ilike', 'IBS')])
    if groups:
        _logger.info("Groups before loading taxes: %s", groups.mapped('name'))
        other_files = [
            "data/l10n_br_fiscal.cst.csv",
            "data/l10n_br_fiscal.tax.csv",
        ]
        _logger.info(_("Loading CSTs and taxes..."))
        for file in other_files:
            tools.convert_file(
                cr,
                "l10n_br_account_nfe_IBSCBS",
                file,
                None,
                mode="init",
            noupdate=True,
            kind="init",
        )