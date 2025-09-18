# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Relatório ponto de venda - tipo venda',
    'version': '16.0',
    'category': 'Sales/Point of Sale',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Relatório POS se tipo de venda',
    'description': """
            Relatórios personalizados para MM Portas
    """,
    'author': 'ATSTi Solucoes',
    'maintainer': 'Carlos Silveira, Mauricio-ATS, ATSTi',
    'website': '',
    'depends': [
        'point_of_sale',
    ],
    'data': [
        'views/pos_order_report_view.xml',
    ],
    'installable': True,
    'application': False,
}
