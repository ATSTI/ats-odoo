# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Data de Pagamento na Tree da Fatura',
    'version': '18.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Exibe datas de pagamento e vencimento na tree da fatura',
    'description': """
        adiciona colunas novas na tree view da fatura, para mostrar a data de pagamento e a data de vencimento da fatura.
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'OtavioAndretta, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': [
        'base',
        'account',
    ],
    'data': [
        'views/account_move.xml',    ],
    'installable': True,
    'application': False,
}
