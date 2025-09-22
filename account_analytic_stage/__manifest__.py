# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See https://www.gnu.org/licenses/agpl

{
    'name': 'Estágio de Contas Analíticas',
    'version': '1.0',
    'category': 'Accounting',
    'license': 'AGPL-3',
    'summary': "Datas e prazos de estágios para Contas Analíticas",
    'description': """
        Esse Módulo Permite o Usuario Financiero Estabelecer estágios para Contas Analíticas
        Data de Início e Data Final.
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': '',
    'depends': ['l10n_br_account', 'analytic'],
    'data': [
        'views/stage.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}