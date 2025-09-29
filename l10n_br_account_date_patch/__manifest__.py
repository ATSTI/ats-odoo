# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Documemnt - Sem Data de Saída',
    'version': '16.0.1.0',
    'category': 'localisation',
    'license': 'AGPL-3',
    'sequence': 7,
    'summary': 'Permite deixar a data de saída vazia',
    'description': """
        Este módulo permite que a date de saida esteja vazia, alguns clientes precisam disso
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': ["l10n_br_account", "l10n_br_nfe",],
    'data': [
        "views/document_view.xml"
    ],
    'installable': True,
    'application': False,
}