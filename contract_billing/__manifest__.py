# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Faturamento Contrato',
    'version': '18.0',
    'category': 'Contract Management',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Faturamento Contrato - ATSTi',
    'description': """
        Esse módulo permite faturar contratos de forma automática,
        gerando faturas com base nos termos e condições definidos
        nos contratos dos clientes.
        OBS: Módulo Usado Pela ATS, com necessidades proprias
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': ['l10n_br_contract'],
    'data': [
        #'views/contract_view.xml',
        'views/email_erro_fatura.xml',
        'views/email_einvoice_template.xml',
        'views/account_invoice.xml',
        'views/sale_view.xml',
    ],
    'installable': True,
    'application': False,
}