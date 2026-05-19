# Copyright (C) 2026 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.ht

{
    'name': 'Controle de Acesso — Condomínio',
    'version': '16.0.1.0.0',
    'summary': 'Gestão de residências, moradores e portaria',
    'category': 'Services',
    'author': 'ATS Soluções',
    'maintainer': 'Otávio Andretta <otavio12257@gmail.com>',
    'depends': ['contacts', 'base','web_widget_image_webcam'],
    'data': [
        'views/security.xml',
        'security/ir.model.access.csv',
        'views/wizard_water_report.xml',
        'views/condo_residence_views.xml',
        'views/condo_residence_leitura.xml',
        'report/report_water_reading_template.xml',
        'views/wizard_water_report_view.xml',
        'views/condo_visitor_view.xml',
        'views/res_partner.xml',
    ],
    'installable': True,
    'application': False,
}   