# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Data na Ordem de Reparo',
    'version': '16.0',
    'category': 'Product',
    'license': 'AGPL-3',
    'summary': 'Opção para definir Data de Ordem no Reparo.',
    'description': """
        Esse Módulo permite definir a data da ordem de reparo
        Adiciona campo data à Ordem de reparo
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': [
        'repair'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/repair_date_view.xml',
    ],
    'installable': True,
    'application': False,
}