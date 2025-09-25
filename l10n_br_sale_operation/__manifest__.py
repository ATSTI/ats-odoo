# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Sale Order - Operação Fiscal Automática',
    'version': '16.0.1.0',
    'category': 'Sales',
    'license': 'AGPL-3',
    'sequence': 6,
    'summary': 'Atualiza automaticamente a Operação Fiscal nas linhas do pedido de venda',
    'description': """
        Este módulo ajusta o comportamento do pedido de venda (Sale Order) para:
        
        - Ao alterar a operação fiscal no pedido, todas as linhas são atualizadas automaticamente;
        - Ao selecionar o cliente, a operação fiscal é definida de acordo com a posição fiscal configurada.
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio Silveira, ATSTi',
    'website': '',
    'depends': [
        'sale_management',
        'l10n_br_fiscal',
    ],
    'data': [],
    'installable': True,
    'application': False,
}