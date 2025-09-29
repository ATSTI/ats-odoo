# Copyright (C) 2025 - ATSTi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'DANFE - Pedido de Venda',
    'version': '16.0.1.0',
    'category': 'Localisation',
    'license': 'AGPL-3',
    'sequence': 5,
    'summary': 'Documento da DANFE dentro do Pedido de Venda',
    'description': """
        Este módulo permite mostrar a DANFE dentro do Pedido de Venda que tenha gerado uma.
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': ["l10n_br_base", "l10n_br_nfe", "l10n_br_account_nfe"],
    'data': [
        "views/sale_view.xml",
    ],
    'installable': True,
    'application': False,
}