# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.ht

{
    'name': 'Customizações Soloz',
    'version': '1.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Módulo de Customizações Específicas para a Soloz',
    'description': """
        Este módulo tem como finalidade algumas mecanicas que a Empresa pediu, entre elas estão:
        - Limitação do responsavel pelo cliente
        - Validação das informações do cliente
        - LogCheatter de alterações no Produto
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': ['base', 'l10n_br_sale', 'l10n_br_purchase', 'sale_project'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_view.xml',
        'views/stock_view.xml',
        'report/sale_report_soloz.xml',
        'report/purchase_report_soloz.xml',
        'wizard/create_task_views.xml',
    ],
    'installable': True,
    'application': False,
}
