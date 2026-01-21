# Copyright (C) 2026 - Mauricio Silveira - ATSti Soluções Tecnológicas
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import os
import csv
import logging

from odoo import SUPERUSER_ID, _, api, tools

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})

    Ncm = env['l10n_br_fiscal.ncm']
    Cfop = env['l10n_br_fiscal.cfop']
    Tax = env['l10n_br_fiscal.tax.classification']

    base_dir = os.path.dirname(__file__)
    csv_path = os.path.join(
        base_dir,
        'data',
        'l10n_br_fiscal.ncm.tax.csv'
    )

    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for i, row in enumerate(reader, start=1):
            ncm = row.get("code", "").strip()
            tax = row.get("tax_classification", "").strip()

            if not ncm or not tax:
                continue

            # extrai número do XML ID
            code_tax = tax.rsplit("_", 1)[-1]

            ncm_record = Ncm.search([('code', '=', ncm)], limit=1)
            tax_record = Tax.search([('code', '=', code_tax)], limit=1)

            if ncm_record and tax_record and not ncm_record.tax_classification_id:
                ncm_record.tax_classification_id = tax_record.id
                _logger.info(
                    "[%s] Linked NCM %s → Tax Classification %s",
                    i, ncm, code_tax
                )

    cfop_to_change = [5901, 6901, 5902, 6902, 5915, 6915]
    cfop_records = Cfop.search([('code', 'in', cfop_to_change)])
    for cfop in cfop_records:
        if cfop.code in ['5901', '6901', '5915', '6915'] and not cfop.tax_classification_id:
            cfop.tax_classification_id = Tax.search([('code', '=', '000000')], limit=1).id
        elif cfop.code in ['5902', '6902'] and not cfop.tax_classification_id:
            cfop.tax_classification_id = Tax.search([('code', '=', '410999')], limit=1).id
        _logger.info(
            "Updated CFOP %s to use tax classification",
            cfop.code
        )