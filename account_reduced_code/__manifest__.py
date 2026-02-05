# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See https://www.gnu.org/licenses/agpl

{
    'name': 'Brazilian Localization Code Reduced',
    'version': '1.0',
    'category': 'Localisation',
    'license': 'AGPL-3',
    'summary': 'Padronização do Código Reduzido para Contabilidade, Parceiros e Produtos.',
    'description': """
Este módulo adiciona e padroniza o uso do **Código Reduzido** nos seguintes modelos:

- Plano de Contas (account.account)
- Parceiros (res.partner)
- Produtos (product.product / product.template)

Funcionalidades:
- Adiciona o campo de Código Reduzido nos registros contábeis.
- Permite manter o mesmo código utilizado na Contabilidade para:
  - Contas contábeis
  - Clientes e fornecedores
  - Produtos
- Facilita a integração com processos contábeis e fiscais.
- Garante maior consistência entre os cadastros operacionais e contábeis.

Ideal para empresas que utilizam código reduzido como referência padrão
em seus processos contábeis e fiscais.
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': [
        'l10n_br_base',
        'l10n_br_account',
        'product',
    ],
    'data': [
        'views/partner_view.xml',
        'views/product_view.xml',
        'views/account.xml',
    ],
    'installable': True,
    'application': False,
}
