# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Ordem de Serviço-Veículos',
    'version': '16.0',
    'category': 'Repair',
    'license': 'AGPL-3',
    'summary': 'Ordem de Serviço-Veículos',
    'description': """
        Altera o modulo repair para utilizar
        para Ordem de Serviço em veículos
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': [
        'base', 'repair', 'stock', 'sale'
    ],
    'data': [
        'views/repair_stage.xml',
        'views/repair_vehicle.xml',
        'views/repair_view.xml',
        'views/res_partner_view.xml',
        'security/ir.model.access.csv'
    ],
    'installable': True,
    'application': False,
}
