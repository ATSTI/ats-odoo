# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Repair Order - Integração com Estoque',
    'version': '16.0.1.0.0',
    'category': 'Operations/Repair',
    'license': 'AGPL-3',
    'summary': 'Gera movimentações de estoque a partir das ordens de reparo',
    'description': """
        Este módulo estende o funcionamento padrão do Odoo no app "Reparos",
        criando movimentos de estoque automáticos durante a finalização das ordens.

        Funcionalidades:
        - Cria movimentos de estoque para os componentes utilizados em reparos.
        - Gera movimentação do produto final reparado para o estoque de destino.
        - Permite rastreamento de lotes/seriais nos movimentos.
        - Integra com o tipo de operação de estoque "Manutenção".
        - Garante consistência de quantidades com verificação de reservas.
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira',
    'website': '',
    'depends': [
        'repair',
        'stock',
    ],
    'data': [],
    'installable': True,
    'application': False,
}
