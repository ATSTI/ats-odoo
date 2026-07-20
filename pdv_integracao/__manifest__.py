# -*- coding: utf-8 -*-
# © 2017 Carlos R. Silveira
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "API integração PDV",
    "version": "10.0.0.0.1",
    "depends": [
        "website",
        "account",
        "point_of_sale",
        "l10n_br_account_due_list"
    ],
    'license': 'AGPL-3',
    "author": "ATS Solucoes, ",
    "category": "sale",
    'data': [
        'views/stock_picking_view.xml',
    ],
    'installable': True,
}
