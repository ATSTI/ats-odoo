# © 2024 Carlos Silveira <crsilveira@gmail.com>
# License AGPL-3.0 or later (http://atsti.com.br).

{  
    'name': 'Atualizando l10n-brazil com dados odoo-brasil na v 14',
    'summary': """Copia informações dos Produtos e Parceiros da odoo-brasil para o l10n-brazil""",
    'description': 'NF-e dados Trustcode',
    'version': '14.0.1.0.0',
    'category': 'account',
    'author': 'ATSTi',
    'license': 'AGPL-3',
    'website': '',
    'contributors': [
        'Carlos Silveira <crsiveira@gmail.com>',
    ],
    'depends': [
        'l10n_br_base', 'account',
    ],
    'data': [
    ],
    "post_init_hook": "post_init_hook",
    'installable': True,
}
