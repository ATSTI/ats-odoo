# Copyright 2020 ATS Soluções
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Controle de Visitas',
    'version': '12.0.0.0.0',
    'category': 'Human Resources',
    'sequence': 80,
    'summary': 'Controle de Visitas Clube',
    'license': 'AGPL-3',
    'author': (
        'ATS Soluções, '
    ),
    'website': 'https://atsti.com.br',
    'installable': True,
    'auto_install': False,
    'depends': [
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/controle_visita_views.xml',
    ],
}
