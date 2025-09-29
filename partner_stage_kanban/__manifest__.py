# Copyright 2025 ATSTi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Partner Stage Kanban',
    'version': '16.0.1.0.0',
    'category': 'Partner',
    'license': 'AGPL-3',
    'summary': 'Adiciona visualização por estágio no Kanban do Parceiro',
    'description': """
Partner Stage Kanban
=====================

Este módulo personaliza a visão Kanban do cadastro de Parceiros (`res.partner`) para:
- Exibir o campo de estágio (`stage_id`);
- Adicionar barra de progresso (`activity_state`);
- Agrupar automaticamente por estágio.
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'contributors': [
        'Carlos Silveira <carlos@atsti.com.br>',
    ],
    'depends': [
        'base',
        'contacts',
    ],
    'data': [
        'views/partner_view.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
}
