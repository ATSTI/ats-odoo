# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'NF-e Danfe: Big FontSize',
    'version': '1.0',
    'category': 'Localisation',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Big FontSize for NF-e Danfe',
    'description': """
        Permite aumentar o tamanho da fonte na impressão da DANFE,
        atraǘes de um checkbox na configuração da empresa.
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': ['l10n_br_nfe'],
    'data': [
        "views/company_views.xml",
    ],
    'installable': True,
    'application': False,
}