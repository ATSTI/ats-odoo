# Copyright (C) 2026 - Mauricio Silveira - ATSti Soluções Tecnológicas
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import os
import csv
import logging

from odoo import SUPERUSER_ID, _, api, tools

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
                if key.startswith('simples') and value == 'SIM':
                    if '101' not in csts:
                        csts.append('101')
                        csts.append('102')
                        csts.append('103')
                        csts.append('201')
                        csts.append('202')
                        csts.append('203')
                        csts.append('300')
                        csts.append('400')
                        csts.append('500')
                        csts.append('900')

            cbenef_record = CBenef.search([('code', '=', row['code'])], limit=1)
            if not cbenef_record:
                cbenef_record = CBenef.create({
                    'code': row['code'],
                    'description': row['descricao'],
                    'icms_cst_ids': [(6, 0, env['l10n_br_fiscal.cst'].search([('code', 'in', csts)]).ids)],
                })
                _logger.info(
                    "Criado cBenef %s com codigo %s e ligado ao(s) CST(s): %s",
                    cbenef_record.description, cbenef_record.code, ', '.join(csts)
                )