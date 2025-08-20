# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Cadastro de Parceiros simplificado',
    'version': '1.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Cadastro de parceiros somente com campos necessario para pequena empresa',
    'description': """
    """,
    'author': 'ATS Soluções',
    'website': '',
    'depends': ['l10n_br_base'],
    'data': [
        'views/partner_view.xml',
    ],
    'installable': True,
    'application': False,
}
