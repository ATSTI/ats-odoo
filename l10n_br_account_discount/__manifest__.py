# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See https://www.gnu.org/licenses/agpl

{
    'name': 'Brazilian Localization Account Discount',
    'version': '16.0',
    'category': 'Localisation',
    'license': 'AGPL-3',
    'summary': 'Permite aplicar um valor total de desconto na fatura, redistribuindo-o automaticamente entre as linhas.',
    'description': """
Este módulo estende o modelo de faturas (account.move) para incluir o campo 
**Total do desconto (amount_discount_value)**.

Funcionalidades:
- Adiciona o campo monetário "Total do desconto" na fatura.
- Permite definir um valor global de desconto na fatura.
- Redistribui automaticamente o valor do desconto proporcionalmente entre as linhas do documento:
  - Baseado no valor de desconto já existente, se houver.
  - Caso contrário, proporcional ao valor bruto das linhas.
- Atualiza os totais da fatura e os impostos após a redistribuição.
- Compatível com o fluxo padrão de recomputação de valores do Odoo.

Ideal para empresas que precisam aplicar descontos globais em faturas 
sem perder o controle da distribuição do desconto em cada item. 
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': [
        'l10n_br_fiscal',
        'l10n_br_account',
    ],
    'data': [
    ],
    'installable': True,
    'application': False,
}