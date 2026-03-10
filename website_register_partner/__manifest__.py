# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Registro de Parceiro via Website',
    'version': '16.0',
    'summary': 'Registro de Parceiro via Website',
    'description': """
Registro de Parceiro via Website
=======================
Registro de Parceiro via Website
    """,
    'category': 'Contacts/Custom',
    'author': 'ATSTi, Odoo Community Association (OCA)',
    'website': 'http://www.atsti.com.br',
    'contributors': [
        'Carlos Silveira <carlos@atsti.com.br>',
        'Mauricio Silveira <maurs320@gmail.com>'
    ],
    'license': 'AGPL-3',
    'depends': [
        'base_setup',
        'contacts',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/curso_view.xml',
        'views/res_partner_view.xml',
    ],
    'demo': [],
    'qweb': [],
    'images': [],
    'sequence': 10,
    'installable': True,
    'application': False,
    'auto_install': False,
}

