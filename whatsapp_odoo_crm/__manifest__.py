# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Integração odoo-whatsapp',
    'version': '18.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'ATSTi Soluções',
    'description': """
            Integração do odoo com whatsapp no crm_leads e demais áreas do odoo
    """,
    'author': 'ATSTi,Odoo Community Association (OCA)',
    'maintainer': 'OtavioAndretta, Mauricio-ATS, ATSTi',
    'website': '',
    'depends': [
        'crm','whatsapp_evolution_base'
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/whatsapp_composer_views.xml',
        'views/crm_leads.xml',
        'views/whatsapp_message_template.xml'
    ],
    'installable': True,
    'application': False,
}