# -*- encoding: utf-8 -*-
##############################################################################
##############################################################################

{
    'name': 'Reparo de Veiculos',
    'description': """
        Campos necessario Soma
    """,
    'version': '1.0',
    'category': 'Localisation',
    'author': 'ATS Solucoes',
    'website': 'http://www.atsti.com.br',
    'license': 'AGPL-3',
    'contributors': [
        'Carlos Silveira<carlos@atsti.com.br>',
    ],
    'depends': [
        'repair', 'stock',
    ],
    'data': [
        'views/repair_stage.xml',
        'views/repair_vehicle.xml',
        'views/repair_views.xml',
        'security/ir.model.access.csv'
    ],
    'demo': [],
    'installable': True,
}
