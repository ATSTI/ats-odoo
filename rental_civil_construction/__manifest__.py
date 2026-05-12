# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Locação Construção Civil',
    'version': '1.0',
    'summary': 'Locação de Equipamentos para Construção Civil',
    'description': """
Locação Construção Civil
========================
Este módulo adiciona campos e funcionalidades relacionadas a locação de equipamentos para construção civil, 
incluindo a gestão de contratos, controle de pagamentos e integração com o módulo de contabilidade. 
Ele é projetado para atender às necessidades específicas do setor de construção civil, 
facilitando a administração e o acompanhamento dos processos de locação.
    """,
    'category': 'Rental',
    'author': 'ATSTi Soluções',
    'maintainer': 'Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'contributors': [
        'Carlos Silveira <carlos@atsti.com.br>',
        'Mauricio Silveira <maurs320@gmail.com>',
        'Otavio Andretta <otavio12257@gmail.com>'
    ],
    'license': 'AGPL-3',
    'depends': ['base_setup', 'web', 'l10n_br_account', 'fieldservice'],
    'data': [
        'report/report_rental_summary.xml',
        'views/product.xml',
        'views/equipment_views.xml',
        'views/account_move.xml',
    ],
    # "assets": {
    #     "web.assets_backend": [
    #         "rental_civil_construction/static/src/js/action_patch.js",
    #     ],
    # },
    'sequence': 10,
    'installable': True,
    'application': False,
    'auto_install': False,
}

