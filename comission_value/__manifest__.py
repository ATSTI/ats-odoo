# -*- coding: utf-8 -*-
#############################################################################

{
    'name': 'Comission Value',
    'version': '14.0.1.1.0',
    'category': 'Sales Management',
    'summary': "Inclui um campo de comissão no Pedido de Venda e na Fatura, Valor colocado representa a comissão do vendedor",
    'author': 'ATSTi Soluções',
    'company': '',
    'website': '',
    'description': """""",
    'depends': [
        'l10n_br_sale',
        'l10n_br_account',
                ],
    'data': [
        'views/sale_view.xml',
        'views/account_invoice_view.xml',
    ],
    'license': 'AGPL-3',
    'application': True,
    'installable': True,
    'auto_install': False,
}
