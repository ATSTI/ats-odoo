# Copyright 2025 ATSTi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Maintenance Request - Integração com Estoque',
    'version': '16.0.1.0',
    'category': 'Maintenance',
    'license': 'LGPL-3',
    'sequence': 12,
    'summary': 'Integra Ordens de Manutenção com o estoque, criando movimentações automáticas',
    'description': """
        Este módulo amplia as Ordens de Manutenção (maintenance.request),
        integrando-as ao módulo de Estoque (stock).

        Funcionalidades:
        - Novo campo de Origem (origin) na Ordem de Manutenção;
        - Possibilidade de vincular um Lote (lot_id) ao equipamento em manutenção;
        - Criação automática de movimentação de estoque ao concluir a manutenção;
        - Mensagem automática no chatter notificando a movimentação gerada.
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    "depends": ["maintenance_request_stage_transition"],
    "data": [
        "views/maintenance_picking_views.xml",
    ],
    'installable': True,
    'application': False,
}