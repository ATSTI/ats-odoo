# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'NF-e Multi Company - Product',
    'version': '16.0.1.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Evita erro de CST em caso de Multi Company',
    'description': """
        Este Módulo permite que em casos de Multi Company, o produto carregue um origem zerado para não dar erro.
        - Se o Produto for de outra empresa, e não dá que está fazendo a nota
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio Silveira, ATSTi',
    'website': '',
    'depends': ['l10n_br_fiscal',],
    'data': [
    ],
    'installable': True,
    'application': False,
}