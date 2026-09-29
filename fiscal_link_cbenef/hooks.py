# Copyright (C) 2026 - Mauricio Silveira - ATSti Soluções Tecnológicas
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import os
import csv
import logging

from odoo import SUPERUSER_ID, _, api, tools

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    CBenef = env['l10n_br_fiscal.tax.definition']
    benefit_field = CBenef._fields['benefit_type']
    regulation = env['l10n_br_fiscal.icms.regulation'].search([('name', '=', 'Regulamento do ICMS')], limit=1)
    base_dir = os.path.dirname(__file__)
    csv_path = os.path.join(
        base_dir,
        'data',
        'Tabela-cBenef-SP-v20260626_uso.csv'
    )

    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        csts = set()
        cbenef_incluidos = set()
        for row in reader:
            if row['codigo'].strip() == 'SEM CBENEF' or row['codigo'].strip() == '':
                continue
            # Simples Nacional
            csts.add('999')
            
            #checar se pega certo o CST
            # CST 00
            for key, value in row.items():
                if not key:
                    continue
                if key.startswith('CST') and value == 'SIM':
                    csts.add(key[3:])
                # if key.startswith('simples') and value == 'SIM':
                #     if '101' not in csts:
                #         csts.append('101')
                #         csts.append('102')
                #         csts.append('103')
                #         csts.append('201')
                #         csts.append('202')
                #         csts.append('203')
                #         csts.append('300')
                #         csts.append('400')
                #         csts.append('500')
                #         csts.append('900')
            print(csts)
            state = env['res.country.state'].search([('name', 'ilike', 'São Paulo')],limit=1,)
            code = row['codigo'].strip()
            _logger.info("Código original: %s", code)
            if not code.startswith(state.code):
                code = f'{state.code}{code}'

            benefit_type = code[3]
            if benefit_type not in dict(benefit_field.selection):
                _logger.warning("Tipo de benefício inválido no código %s: %s",code,benefit_type,)
                continue

            _logger.info("Código após ajuste: %s", code)
            _logger.info("Tamanho do código: %s", len(code))
            # ncm_record = CBenef.search([('code', 'ilike', row['NCMs'])], limit=1)
            # import pudb;pudb.set_trace()
            cbenef_record = CBenef.search([
                ('code', '=', code),
            ], limit=1)
            tax_rn = env['l10n_br_fiscal.tax.group'].search([('name', '=', 'ICMS')],limit=1,)
            # CST 00	CST 02	CST 10	CST 15	CST 20	CST 30	CST 40	CST 41	CST 50	CST 51	CST 53	CST 60	CST 61	CST 70	CST 90
            # import pudb;pu.db
            if not cbenef_record:
                for cst in csts:
                    # import pudb;pu.db
                    if cst == '999':
                        tax_simple = env['l10n_br_fiscal.tax.group'].search([('name', '=', 'ICMS - Simples Nacional')],limit=1,)
                        cst_id = env['l10n_br_fiscal.cst'].search([
                            ('code', '=', '900'),
                            ('tax_group_id', '=', tax_simple.id)
                        ])
                        tax_group = tax_simple
                    else:
                        tax_group = tax_rn
                        cst_id = env['l10n_br_fiscal.cst'].search([
                            ('code', '=', cst),
                            ('tax_group_id', '=', tax_group.id)
                        ])
                    tax_id = env['l10n_br_fiscal.tax'].search([
                        ('cst_out_id', '=', cst_id.id),
                        ('tax_group_id', '=', tax_group.id)
                    ])
                    if code not in cbenef_incluidos:
                        cbenef_record = CBenef.create({
                            'tax_group_id': tax_group.id,
                            'tax_domain': tax_group.tax_domain,
                            'tax_id': tax_id.id,
                            'cst_id': cst_id.id,
                            'cst_code': cst_id.code,
                            'is_benefit': True,
                            'state_from_id': state.id,
                            'code': code,
                            'description': f"{code} - {row['descricao']}",
                            'name': f"{code} - {row['descricao']}",
                            'benefit_type': benefit_type,
                            'ncms': row['ncms'],
                            'icms_regulation_id': regulation.id,
                            'state': 'approved',
                        })
                        cbenef_incluidos.add(code)
            # else:
            #     cbenef_incluidos.add(code)
            #     cbenef_record.write({
            #         'is_benefit': True,
            #         'icms_regulation_id': regulation.id,
            #         'ncms': row['ncms'],
            #     })
            _logger.info(
                "Criado cBenef %s com codigo %s e ligado ao(s) CST(s) e NCMs: %s",
                cbenef_record.description, cbenef_record.code, ', '.join(csts))
            cbenef_record.action_review()
            cbenef_record.action_approve()
                



#hook antigoi, deixando aqui como referencia pro novo hook q linka ao ncm
# def post_init_hook(cr, registry):
#     env = api.Environment(cr, SUPERUSER_ID, {})

#     CBenef = env['l10n_br_fiscal.icms.cbenef']

#     base_dir = os.path.dirname(__file__)
#     csv_path = os.path.join(
#         base_dir,
#         'data',
#         'Tabela-cBenef-SP-v20260626_uso.ods'
#     )

#     with open(csv_path, newline='', encoding='utf-8') as f:
#         reader = csv.DictReader(f)
#         for row in reader:
#             csts = []

#             for key, value in row.items():
#                 if not key:
#                     continue
#                 if key.startswith('cst') and value == 'SIM':
#                     csts.append(key[3:])
#                 if key.startswith('simples') and value == 'SIM':
#                     if '101' not in csts:
#                         csts.append('101')
#                         csts.append('102')
#                         csts.append('103')
#                         csts.append('201')
#                         csts.append('202')
#                         csts.append('203')
#                         csts.append('300')
#                         csts.append('400')
#                         csts.append('500')
#                         csts.append('900')

#             cbenef_record = CBenef.search([('code', '=', row['code'])], limit=1)
#             if not cbenef_record:
#                 cbenef_record = CBenef.create({
#                     'code': row['code'],
#                     'description': row['descricao'],
#                     'icms_cst_ids': [(6, 0, env['l10n_br_fiscal.cst'].search([('code', 'in', csts)]).ids)],
#                 })
#                 _logger.info(
#                     "Criado cBenef %s com codigo %s e ligado ao(s) CST(s): %s",
#                     cbenef_record.description, cbenef_record.code, ', '.join(csts)
#                 )