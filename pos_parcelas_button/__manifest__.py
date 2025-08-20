# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Botão de POS',
    'version': '1.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Colocar botão no pos',
    'description': """
        Colocar botão no pos
    """,
    'author': 'ATS Soluções',
    'website': '',
    'depends': ['base', 'point_of_sale'],
    'qweb': [
        'static/src/xml/parcelas_button.xml',
    ],
    'data': [
        'views/view.xml'
    ],
    'installable': True,
    'application': False,
}
