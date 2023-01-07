# Copyright 2021 Atsti - Mauricio Silveira
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Contrato Corretora',
    'summary': 'Controle de apolices de seguro',
    'version': '12.0.1.0.0',
    'category': 'Contract Management',
    'website': 'https://github.com/oca/contract',
    'author': 'Atsti, '
              'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'installable': True,
    'depends': [
        'contract_novo',
    ],
    'data': [
        'views/contract_view.xml',
    ],
}
