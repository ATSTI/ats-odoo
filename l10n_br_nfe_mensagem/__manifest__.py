# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'NF-e Mensagens',
    'version': '1.0',
    'category': 'Localisation',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Mensagem Erro NFe',
    'description': """
        Adiciona mensagem de validação campos obrigatórios do cliente
        na fatura, e deixa algumas msg de validação da nfe mais fáceis,
        e exibe na fatura as mensagens de validaçao.
        Além disso, esse módulo evita o erro de certificado expirado e exibe uma mensagem de erro mais amigável para o usuário.
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': ['l10n_br_account','l10n_br_nfe', 'l10n_br_fiscal_certificate'],
    'data': [
        "views/account_invoice_view.xml",
    ],
    'installable': True,
    'application': False,
}