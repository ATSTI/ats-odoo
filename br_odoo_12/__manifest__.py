# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{  
    'name': 'Odoo Brasil Dados',
    'version': '16.0.1.0',
    'category': 'Localisation',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Permite manter histórico das NF-e emitidas pelo modulo odoo-brasil',
    'description': """
        NF-e - odoo-brasil, Dados da NFE para migração de versões do ODOO
        para clientes migrado odoo 12 para odoo 16
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': '',
    'depends': [
        'base', 'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_fiscal_position.xml',
        'views/br_odoo_nfe_view.xml',
        'views/br_odoo_nfe_item_view.xml',
        'views/partner_view.xml',
        'views/product_view.xml',
    ],
    "post_init_hook": "post_init_hook",
    'installable': True,
}
