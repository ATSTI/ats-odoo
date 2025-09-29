# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Brazilian Localization CNPJF/CPF Consulta',
    'version': '16.0.1.0',
    'category': 'localisation',
    'license': 'AGPL-3',
    'sequence': 7,
    'summary': 'Módulo de consulta CNPJ / CPF , que traz IE',
    'description': """
        Diferente do módulo da OCA/l10n-brazil , este módulo trás também as informações da Inscrição Estadual (IE) da Empresa
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': ['l10n_br_base',],
    'data': [
        "views/res_partner_view.xml",
    ],
    'installable': True,
    'application': False,
}