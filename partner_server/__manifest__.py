# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Informações de Servidor',
    'version': '1.0',
    'category': 'Res Partner',
    'author': 'ATS Solucoes',
    'website': 'http://www.atsti.com.br',
    'license': 'AGPL-3',
    'contributors': [
        'Carlos Silveira<carlos@atsti.com.br>',
        'Mauricio Silveira<maurs320@gmail.com>',
        'Otavio Andretta<otavio12257@gmail.com>'
    ],
    'depends': [
        'base_setup','nfe_integracao'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_view.xml',
    ],
    'demo': [],
    'installable': True,
}

