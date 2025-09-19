# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.ht

{
    'name': 'Integração Estoque e Reparos',
    'version': '1.0',
    'category': 'Inventory/Stock',
    'license': 'AGPL-3',
    'sequence': 5,
    'summary': 'Gera ordens de reparo a partir de entradas de estoque',
    'description': """
        Este módulo estende o comportamento das operações de estoque para integrar
        automaticamente com o módulo de reparos.

        Funcionalidades principais:
        - Ao validar uma entrada de estoque (picking de tipo "IN"), 
          é criada uma **ordem de reparo**.
        - A ordem é vinculada ao **produto**, **lote**, **quantidade recebida** e **local de destino**.
        - Permite rastreabilidade entre recebimento de produtos e processos de reparo.

        Futuras melhorias:
        - Filtrar por tipos específicos de Picking.
        - Preencher informações adicionais como responsável, datas e método de faturamento.
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': '',
    'depends': ['stock', 'repair'],
    'data': [],
    'installable': True,
    'application': False,
}