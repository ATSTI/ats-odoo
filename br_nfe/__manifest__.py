# © 2024 Carlos Silveira <crsilveira@gmail.com>, Trustcode
# License AGPL-3.0 or later (http://atsti.com.br).

{  # pylint: disable=C8101,C8103
    'name': 'Envio de NF-e',
    'summary': """Permite o envio de NF-e através das faturas do Odoo
    Mantido por Trustcode""",
    'description': 'Envio de NF-e',
    'version': '14.0.1.0.0',
    'category': 'account',
    'author': 'Trustcode',
    'license': 'AGPL-3',
    'website': 'http://www.trustcode.com.br',
    'contributors': [
        'Carlos Silveira <crsiveira@gmail.com>',
    ],
    'depends': [
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_fiscal_position.xml',
        'views/invoice_eletronic.xml',
        'views/invoice_eletronic_item.xml',
        'views/br_nfe.xml',
        'views/br_account_view.xml',
    ],
    'installable': True,
    'application': True,
}
