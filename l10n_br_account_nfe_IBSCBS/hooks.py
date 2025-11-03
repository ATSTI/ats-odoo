import logging
import csv

import os

from odoo import SUPERUSER_ID, _, api, tools

_logger = logging.getLogger(__name__)

def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    module_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(module_dir, 'data', 'l10n_br_fiscal.tax.csv')
    novos_itens = []
    with open(file_path, 'r', encoding='utf-8') as file: # Use appropriate encoding
        csv_data = csv.DictReader(file) 
        for row in csv_data:
            novos_itens.append(row)
    ir_model_data_obj = env['ir.model.data']
    # Search for an existing entry
    for item in novos_itens:
        existing_data = ir_model_data_obj.search([
            ('module', '=', 'l10n_br_account_nfe_IBSCBS'),
            ('name', '=', item["id"]),
        ])

        if existing_data:
            continue
        else:
            # Create a new entry
            id_cst = ir_model_data_obj.search([
                ("module", "=", "l10n_br_account_nfe_IBSCBS"),
                ("name", "=", item["cst_out_id"]),
            ])
            id_tax_group = ir_model_data_obj.search([
                ("module", "=", "l10n_br_account_nfe_IBSCBS"),
                ("name", "=", item["tax_group_id"]),
            ])
            group = env["account.tax.group"].search([
                ("name", "=", id_tax_group.name)
            ])
            if not group:
                group = env["account.tax.group"].create({
                    "name": id_tax_group.name,
                    "fiscal_tax_group_id": id_tax_group.res_id
                })
            if not group.fiscal_tax_group_id:
                group.write({"fiscal_tax_group_id": id_tax_group.res_id})

            tax_new = item
            id_grp = item["id"]

            del tax_new["id"]
            del tax_new["cst_in_id"]
            tax_new["tax_group_id"] = id_tax_group.res_id
            tax_new["cst_out_id"] = id_cst.res_id
            
            id_model = env["l10n_br_fiscal.tax"].create(tax_new)

            ir_model_data_obj.create({
                'module': "l10n_br_account_nfe_IBSCBS",
                'name': id_grp,
                'model': 'l10n_br_fiscal.tax',
                'res_id': id_model.id,
                "noupdate": True,
            })

            _logger.info(_("item incluido com sucesso. %s" %(id_grp)))

    "preenche informacoes do IBSCBS"
    empresas = env['res.company'].search([
        ('ibscbs_cst_id', '=', False)
    ])
    
    _logger.info(_("Atualizando dados da empresa..."))
    for empresa in empresas:
        id_cst = ir_model_data_obj.search([
            ("module", "=", "l10n_br_account_nfe_IBSCBS"),
            ("name", "=", "cst_ibscbs_000001"),
        ])
        id_uf_tax = ir_model_data_obj.search([
            ("module", "=", "l10n_br_account_nfe_IBSCBS"),
            ("name", "=", "tax_ibsuf_000001"),
            ("model", "=", "l10n_br_fiscal.tax"),
        ])
        id_mun_tax = ir_model_data_obj.search([
            ("module", "=", "l10n_br_account_nfe_IBSCBS"),
            ("name", "=", "tax_ibsmun_000001"),
            ("model", "=", "l10n_br_fiscal.tax"),
        ])
        id_cbs_tax = ir_model_data_obj.search([
            ("module", "=", "l10n_br_account_nfe_IBSCBS"),
            ("name", "=", "tax_cbs_000001"),
            ("model", "=", "l10n_br_fiscal.tax"),
        ])
        
        empresa.write({
            "ibscbs_cst_id": id_cst.res_id,
            "ibsuf_tax_id": id_uf_tax.res_id,
            "ibsmun_tax_id": id_mun_tax.res_id,
            "cbs_tax_id": id_cbs_tax.res_id,
        })
    _logger.info(_("Empresas atualizadas com sucesso..."))
