# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Cadastro de Contatos Simplificado',
    'version': '16.0.1.0',
    'category': 'Human Resources',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Cadastro de Contato com tela mais simplificada, alvo: Pequenas Empresas',
    'description': """
        Este Módulo Simplifica a tela de Cadastro de Contato, permitindo menor poluição visual.
        Uso recomendado para pequenas empresas
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': ['l10n_br_base'],
    'data': [
        'views/partner_view.xml',
    ],
    'installable': True,
    'application': False,
}
