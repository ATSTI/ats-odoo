# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Contracts Management - Date recurring',
    'version': '16.0.1.0',
    'category': 'Contract Management',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Calculo da proxima Data de Vencimento',
    'description': """
        Este Módulo adiciona novas funções para o Contrato:
        - Calculo da proxima data de vencimento nas faturas
        - Marcadores do contrato (fatura e venda)
    """,
    'author': 'ATSTi Soluções',
    'website': '',
    'depends': ['l10n_br_account', 'contract', 'sale_management'],
    'data': [
        "views/account.xml",
        "views/sale_view.xml",
    ],
    'installable': True,
    'application': False,
}
