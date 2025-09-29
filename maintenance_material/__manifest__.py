# Copyright (C) 2025 - ATSTi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0.html)

{
    'name': 'Maintenance Request - Custos de Materiais',
    'version': '16.0.1.0',
    'category': 'Maintenance',
    'license': 'AGPL-3',
    'sequence': 11,
    'summary': 'Adiciona controle de materiais e custos às Ordens de Manutenção',
    'description': """
        Este módulo expande a funcionalidade de Ordens de Manutenção (maintenance.request),
        permitindo lançar os materiais utilizados na manutenção com seus respectivos custos.

        Funcionalidades:
        - Adiciona aba de materiais usados na Ordem de Manutenção;
        - Controle de produto, quantidade, unidade e preço unitário;
        - Cálculo automático do subtotal por linha e do total da manutenção;
        - Integração com moeda da empresa.
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    "depends": ["maintenance_product"],
    "data": [
        "security/ir.model.access.csv",
        "views/maintenance_view.xml"
    ],
    'installable': True,
    'application': False,
}