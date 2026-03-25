# Copyright (C) 2026 - Mauricio Silveira - ATSti Soluções Tecnológicas
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import os
import csv
import logging

from odoo import SUPERUSER_ID, _, api

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})

    CBenef = env['l10n_br_fiscal.icms.cbenef']

    base_dir = os.path.dirname(__file__)
    csv_path = os.path.join(
        base_dir,
        'data',
        'l10n_br_fiscal.icms.cbenef.csv'
    )

    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            csts = []

            for key, value in row.items():
                if not key:
                    continue
                if key.startswith('cst') and value == 'SIM':
                    csts.append(key[3:])

            for cst in csts:
                cbenef_record = CBenef.search([
                    ('code', '=', row['code']),
                    ('cst', '=', cst)
                ], limit=1)

                if not cbenef_record:
                    cbenef_record = CBenef.create({
                        'code': row['code'],
                        'description': row['descricao'],
                        'cst': cst,
                    })
                _logger.info(
                    "Criado cBenef %s com codigo %s e ligado ao(s) CST(s): %s",
                    cbenef_record.description, cbenef_record.code, ', '.join(csts)
                )
