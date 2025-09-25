# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Account Move - Operação Fiscal Automática',
    'version': '16.0.1.0',
    'category': 'Accounting',
    'license': 'AGPL-3',
    'sequence': 9,
    'summary': 'Atualiza automaticamente a Operação Fiscal nas linhas da fatura',
    'description': """
        Este módulo ajusta o comportamento das faturas (Account Move) para:
        
        - Ao alterar a operação fiscal na fatura, todas as linhas são atualizadas automaticamente;
        - Ao selecionar o cliente, a operação fiscal é definida de acordo com a posição fiscal configurada.
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio Silveira, ATSTi',
    'website': '',
    'depends': ['account','l10n_br_fiscal',],
    'data': [
    ],
    'installable': True,
    'application': False,
}
