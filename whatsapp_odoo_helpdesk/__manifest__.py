# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Integração odoo-whatsapp com helpdesk',
    'version': '18.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Odoo WhatsApp Helpdesk Integration',
    'description': """
            Integração do odoo com whatsapp no helpdesk e demais áreas do odoo
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'OtavioAndretta, Mauricio-ATS, ATSTi',
    'website': '',
    'depends': [
        'helpdesk_mgmt','whatsapp_evolution_base','whatsapp_evolution_discuss'
    ],
    'data': [
        "views/helpdesk_ticket_btn.xml"

    ],
    'installable': True,
    'application': False,
}