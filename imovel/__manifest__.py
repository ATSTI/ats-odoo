# -*- coding: utf-8 -*-
# © 2004-2010 OpenERP SA
# © 2019 Carlos Silveira <crsilveira@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Imovel',
    'version': '14.0.1.0.0',
    'category': 'Product',
    'author': 'Carlos R. Silveira '
              ,
    'license': 'AGPL-3',
    'depends': ['account', 'product', 'l10n_br_base', 'l10n_br_zip', 'contract', 'contract_state'],
    'data': [
        'views/imovel_view.xml',
        'views/contract_view.xml',
        'views/account_invoice_view.xml',
        'views/ir_sequence_data.xml',
        # 'views/report_invoice_document.xml',
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        ],
    'installable': True,
    'images': [
        'static/description/icon.png',
    ],
}
