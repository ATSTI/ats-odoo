# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.ht

{
    'name': 'Integração Estoque e Manutenção',
    'version': '1.0',
    'category': 'Inventory/Stock',
    'license': 'AGPL-3',
    'sequence': 4,
    'summary': 'Gera solicitações de manutenção preventiva a partir de entradas de estoque',
    'description': """
        Este módulo estende o comportamento das operações de estoque para integrar
        automaticamente com o módulo de manutenção.

        Funcionalidades principais:
        - Ao validar uma entrada de estoque (picking de tipo "IN"), 
          é criada uma **solicitação de manutenção preventiva**.
        - A solicitação é vinculada ao **equipamento** relacionado ao produto e ao **lote** movimentado.
        - Garante rastreabilidade e integração entre estoque e manutenção.

        Futuras melhorias:
        - Definir responsável automaticamente.
        - Agendamento da data de manutenção conforme parâmetros do produto/equipamento.
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': ['stock', 'maintenance_product', 'maintenance_picking'],
    'data': [],
    'installable': True,
    'application': False,
}