# -*- coding: utf-8 -*-
# © 2017 Otávio Silveira Munhoz <otaviosilmunhoz@hotmail.com>, ATSTI
# © 2018 Carlos Rodrigues Silveira <crsilveira@gmail.com>, ATSTI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{
    'name': 'Importação de Documento Fiscal Eletronico de Compras',
    'version': '10.0.1.0.0',
    'category': 'Account addons',
    'license': 'AGPL-3',
    'author': 'ATSTI',
    'website': 'https://www.atsti.com.br',
    'depends': [
        'purchase',
        'br_purchase',
    ],
    'data': [
        'wizard/import_nfe.xml',
        'wizard/import_nfe_sale.xml',
        'views/purchase_view.xml',
        'views/account_invoice.xml',
    ],
}
