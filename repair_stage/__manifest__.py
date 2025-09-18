# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Estágio na Ordem de Serviço',
    'version': '16.0',
    'category': 'Repair',
    'license': 'AGPL-3',
    'summary': 'Adiciona kanban de estágio na OS',
    'description': """
        Adiciona kanban de estágio na OS
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos Silveira, Mauricio-ATS, ATSTi',
    'website': '',
    'depends': [
        'base', 'repair', 'stock', 'sale'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/repair_stage_data.xml',
        'views/repair_stage.xml',
        'views/repair_view.xml',
    ],
    'installable': True,
    'application': False,
}
