# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Faturamento do Contrato',
    'version': '16.0.1.0',
    'category': 'Contract Management',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Permite fazer o faturamento de contratos',
    'description': """
        Este Módulo possibilita fazer apartir de um contrato, o seu respectivo faturamento
    """,
    'author': 'Carlos Silveira, Mauricio-ATS, ATSTi Soluções',
    'website': '',
    'depends': ['l10n_br_contract','l10n_br_account', 'l10n_br_account_payment_brcobranca'],
    'data': [
        #'views/contract_view.xml',
        'views/email_erro_fatura.xml',
        'views/email_einvoice_template.xml',
        'views/account_invoice.xml'
    ],
    'installable': True,
    'application': False,
}

