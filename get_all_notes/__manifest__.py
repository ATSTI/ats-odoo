# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Notas por Empresa - Relatórios',
    'version': '16.0.1.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Visualização / Relatório para total de notas',
    'description': """
        Este Módulo mostra o total de notas que uma empresa emitiu:
        - Visualização
        - Relatório
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': ['base', 'sale', 'l10n_br_fiscal', 'l10n_br_account',],
    'data': [
        'report/all_note_report_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
}

