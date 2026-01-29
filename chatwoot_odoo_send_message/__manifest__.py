# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Integração Chatwoot-Odoo / Envio de Mensagens',
    'version': '18.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Odoo Chatwoot CRM Integration',
    'description': """
            Integração do odoo com chatwoot no crm_leads e demais áreas do odoo
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'OtavioAndretta, Mauricio-ATS, ATSTi',
    'website': '',
    'depends': [
        'crm','chatwoot_odoo'
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/chatwoot_composer_views.xml',
        'views/crm_leads.xml',
        'views/partner_view.xml',
        'views/move_view.xml',
        'views/chatwoot_message_template.xml'
    ],
    'installable': True,
    'application': False,
}