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
    'depends': ['base', 'account', 'product', 'l10n_br_base', 'l10n_br_zip', 'contract', 'contract_state'],
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'views/imovel_view.xml',
        'views/contract_view.xml',
        'views/account_invoice_view.xml',
        'views/ir_sequence_data.xml',
        'wizard/imovel_alugarvender.xml',
        # 'views/report_invoice_document.xml',
        ],
    'installable': True,
    'images': [
        'static/description/icon.png',
    ],
}
