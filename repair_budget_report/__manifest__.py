# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Cotação por Reparos',
    'version': '16.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Impressão de Cotação',
    'description': """
    """,
    'author': 'ATSTi Soluções',
    'website': '',
    'depends': ['repair_date','repair'],
    'data': [
        'report/repair_templates_repair_order.xml',

    ],
    'installable': True,
    'application': False,
}
