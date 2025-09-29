# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Outros Controles para o Contrato',
    'version': '16.0.1.0',
    'category': 'Contract',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Disponibilidade de outros comando para o contrato',
    'description': """
        Este Módulo adiciona novas funções para o Contrato, baseando no envio de email e datas
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': ['contract', 'analytic',],
    'data': [
        # "views/contract_view.xml",
    ],
    'installable': True,
    'application': False,
}
