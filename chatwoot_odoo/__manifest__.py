# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Odoo - Chatwoot',
    'version': '18.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Integração Odoo com Chatwoot',
    'description': """
Integração Odoo com Chatwoot
Este módulo adiciona campos e funcionalidades relacionadas a dados de conversas 
associadas ao helpdesk, permitindo registro de conversas do Chatwoot como tickets no Odoo.
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': [
        'base_setup',
        'helpdesk_mgmt'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/chatwoot_view.xml',
        'views/helpdesk_view.xml',
    ],
    'installable': True,
    'application': False,
}
