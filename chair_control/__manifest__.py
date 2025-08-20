# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Controle de cadeiras',
    'version': '1.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'controle de cadeiras',
    'description': """
    """,
    'author': 'otaviosilmunhoz@hotmail.com/ATS Soluções',
    'website': '',
    'depends': ['event_sale', 'point_of_sale'],
    'data': [
            'views/chair_view.xml',
            'views/event_view.xml',
            'report/chair_template.xml',
            'report/event_template.xml',
            'security/ir.model.access.csv'
    ],
    'installable': True,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
