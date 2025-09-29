# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Desconto no Total da Compra',
    'version': '16.0',
    'category': 'Purchase',
    'license': 'AGPL-3',
    'summary': 'Desconto no valor total da compra',
    'description': """
            Desconto no Total da Compra
=======================
Módulo para gerenciar desconto no valor total da compra.
        como um valor específico ou percentual
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': [
        'l10n_br_purchase',
        'account_discount_total',
        'l10n_br_delivery',
    ],
    'data': [
        'views/purchase_view.xml',
        'views/purchase_order_report.xml',
        # 'views/res_config_view.xml',
    ],
    'installable': True,
    'application': False,
}
