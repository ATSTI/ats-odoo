# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Contrato - Responsável Faturamento',
    'version': '16.0.1.0',
    'category': 'Contract Management',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Define o responsavel pelo faturamento',
    'description': """
        Este Módulo adiciona novas funções para o Contrato:
        - Campo do responsável pelo faturamento
        - Criação de faturas para tal responsável
    """,
    'author': 'ATSTi Soluções',
    'website': '',
    'depends': ["contract", "l10n_br_fiscal", "l10n_br_account_payment_brcobranca", "contract_recurring_date"],
    'data': [
        "views/contract_view.xml",
    ],
    'installable': True,
    'application': False,
}

