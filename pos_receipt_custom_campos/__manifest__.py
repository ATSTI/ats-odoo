# Copyright (C) 2025 - ATSTi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Recibo POS - Campos',
    'version': '16.0.1.0.0',
    'category': 'Point Of Sale',
    'license': 'AGPL-3',
    'sequence': 10,
    'summary': 'Personalização do recibo do POS - Cliente: Campos',
    'description': """
        Módulo Personaliza o Recibo impresso no Ponto de Venda, o Cliente dessa customização é o Campos
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': ['point_of_sale'],
    'data': [
    ],
    'qweb': [
        'static/src/xml/OrderReceipt.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}