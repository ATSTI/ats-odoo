# © 2024 Carlos Silveira <crsilveira@gmail.com>
# License AGPL-3.0 or later (http://atsti.com.br).

{  
    'name': 'Mantendo dados odoo-brasil para odoo 14',
    'summary': """Permite manter histórico das NF-e emitidas pelo modulo odoo-brasil(TrustCode)""",
    'description': 'NF-e dados Trustcode',
    'version': '12.0.1.0.0',
    'category': 'account',
    'author': 'ATSTi',
    'license': 'AGPL-3',
    'website': '',
    'contributors': [
        'Carlos Silveira <crsiveira@gmail.com>',
    ],
    'depends': [
        'base', 'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_fiscal_position.xml',
        'views/br_odoo_nfe_view.xml',
        'views/br_odoo_nfe_item_view.xml',
        # 'views/br_nfe.xml',
        # 'views/br_account_view.xml',
        'views/partner_view.xml',
        'views/product_view.xml',
    ],
    "post_init_hook": "post_init_hook",
    'installable': True,
}