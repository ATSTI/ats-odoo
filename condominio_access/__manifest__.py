# Copyright (C) 2026 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.ht

{
    'name': 'Controle de Acesso — Condomínio',
    'version': '16.0.1.0.0',
    'summary': 'Gestão de residências, moradores e portaria',
    'category': 'Services',
    'author': 'ATS Soluções',
    'maintainer': 'Otávio Andretta <otavio12257@gmail.com>',
    'depends': ['contacts', 'base','web_widget_image_webcam', 'helpdesk_mgmt'],
    'data': [
        'views/security.xml',
        'security/ir.model.access.csv',
        'views/res_partner.xml',
        'views/wizard_water_report.xml',
        'report/report_water_not_found_template.xml',
        'report/helpdesk_ticket_report.xml',
        'views/condo_residence_views.xml',
        'views/condo_residence_leitura.xml',
        'report/report_water_reading_template.xml',
        'views/wizard_water_report_view.xml',
        'views/condo_visitor_view.xml',
        'views/helpdesk_ticket_view.xml',
        'views/wizard_cancelar_visita.xml',
    ],
    'installable': True,
    'application': False,
}   