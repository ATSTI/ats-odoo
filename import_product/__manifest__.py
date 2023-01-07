# -*- coding: utf-8 -*-
# © 2004-2010 OpenERP SA
# © 2016 Carlos R Silveira <crsilveira@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Importar Planilhas',
    'version': '1.0',
    'author': 'ATS Solucoes',
    'description': '''Import csv files''',
    'website': 'http://www.atsti.com.br/',
    'category': 'Contract Management',
    'depends': [
        'base', 'sale','product'
    ],
    'data':  [
        'views/import_product_view.xml',
    ],
    'installable': True,
    'images': [],

}

