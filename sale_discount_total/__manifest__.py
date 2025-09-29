# Copyright (C) 2025 - ATSTi
# License AGPL-3 - Veja https://www.gnu.org/licenses/agpl

{
    'name': 'Desconto sobre o Valor Total de Venda',
    'version': '16.0',
    'category': 'Gestão de Vendas',
    'license': 'AGPL-3',
    'summary': 'Desconto no total em Vendas e Faturas com limite de desconto e aprovação (adaptado do módulo Cybrosys l10n-brazil)',
    'description': """
        Desconto sobre o valor total de vendas.
        Módulo para gerenciar desconto sobre o valor total em vendas,
        seja como valor específico ou percentual.
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': [
        'l10n_br_sale',
        'sale_discount_display_amount',
        'account_discount_total',
        'l10n_br_delivery',
    ],
    'data': [
        'views/sale_view.xml',
        # 'views/sale_order_report.xml',
        'views/res_config_view.xml',
    ],
    'installable': True,
    'application': False,
}