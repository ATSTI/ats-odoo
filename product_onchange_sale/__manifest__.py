# Copyright (C) 2026 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Onchange de produtos na fatura e pedido de venda',
    'version': '1.0',
    'category': 'Localisation',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Onchange de produtos na fatura e pedido de venda',
    'description': """
Onchange de produtos na fatura e pedido de venda
=======================
Este módulo adiciona um onchange de produtos, ao alterar no pedido de venda, ele altera automaticamente na FATURA sem comprometer a integridade dos dados fiscais principalmente
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'OtavioAndretta, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': [
        'l10n_br_fiscal',
        'l10n_br_account',
        'l10n_br_nfe',
    ],
    'data': [
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
}