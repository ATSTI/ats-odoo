# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Teste Alternar empresa',
    'version': '1.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'alternar empresa',
    'description': """
    """,
    'author': 'ATS Soluções',
    'website': '',
    'depends': ['sale'],
    'data': [
        'views/company_switch.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'static/src/js/load_js_function.js',
        ],
    },
    'installable': True,
    'application': False,
}
