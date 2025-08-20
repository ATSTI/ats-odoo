# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Cadastro de Parceiros nao aparece o CEP nesta base',
    'version': '1.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Cadastro de parceiros ',
    'description': """
    """,
    'author': 'ATS Soluções',
    'website': '',
    'depends': ['l10n_br_base', 'l10n_br_zip'],
    'data': [
        'views/partner_view.xml',
    ],
    'installable': True,
    'application': False,
}
