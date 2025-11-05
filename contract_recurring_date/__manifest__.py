# Copyright (C) 2025 - ATSTi
# License AGPL-3 - Veja https://www.gnu.org/licenses/agpl

{
    'name': 'Recurring - Contracts Management - Date Recurring',
    'version': '18.0',
    'category': 'Contract Management',
    'license': 'AGPL-3',
    'summary': 'Gestão de contratos recorrentes com controle de datas',
    'description': """
        Módulo para gerenciamento de contratos recorrentes,
        adicionando controle sobre as datas de recorrência em
        vendas e faturas.
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': [
        'contract',
        'sale_management',
    ],
    'data': [
        'views/account.xml',
        'views/sale_view.xml',
    ],
    'installable': True,
    'application': False,
}