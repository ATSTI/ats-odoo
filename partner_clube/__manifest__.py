# Copyright 2025 ATSTi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Associações e Clubes',
    'version': '16.0.1.0.0',
    'category': 'Partner',
    'license': 'AGPL-3',
    'summary': 'Campos adicionais para Associações e Clubes',
    'description': """
Campos adicionais para Associações e Clubes

Este módulo adiciona campos extras no cadastro de parceiros (contacts)
para controle e gestão de associações e clubes.
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': ['l10n_br_base','contacts',],
    'data': [
        'security/ir.model.access.csv',
        'views/partner_view.xml',
        'views/partner_categoria_view.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
}